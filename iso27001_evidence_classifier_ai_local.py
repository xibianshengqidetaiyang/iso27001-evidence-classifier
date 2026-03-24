#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO27001 证据分类 + AI 初步审核脚本
---------------------------------
在原有 iso27001_evidence_classifier.py 基础上增加：
1. 规则分类（many-to-many）
2. 仅对候选命中项做 AI 初步审核
3. 输出结构化 JSON / CSV / Markdown 审核意见

支持的 AI 提供方（OpenAI 兼容协议）：
- Ollama 本地模型（默认 base_url: http://localhost:11434/v1/）
- DeepSeek（默认 base_url: https://api.deepseek.com）
- 豆包/火山方舟（默认 base_url: https://ark.cn-beijing.volces.com/api/v3）

示例：
python iso27001_evidence_classifier_ai.py \
  --evidence-dir ./evidence \
  --output-dir ./output_ai \
  --handbooks ./ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md ./ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md \
  --enable-ai \
  --ai-provider ollama \
  --ai-model llama3.2:1b

环境变量：
- Ollama 本地模型：无需真实 API Key（OpenAI SDK 中 api_key='ollama' 即可）
- DeepSeek: DEEPSEEK_API_KEY
- 豆包/火山方舟: ARK_API_KEY

说明：
- AI 只做“初步审核意见”，不直接替代人工最终结论。
- 建议先对脱敏后的证据使用 API。
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# 复用原脚本中的规则提取、文件读取、规则分类能力
import iso27001_evidence_classifier as base

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


DEFAULT_AI_DOC_TOPK = 3
DEFAULT_AI_MIN_RULE_SCORE = 4.5
DEFAULT_AI_MAX_CONTEXT_CHARS = 5000
DEFAULT_AI_TIMEOUT = 120


@dataclasses.dataclass
class AIAuditResult:
    file_path: str
    control_id: str
    title_cn: str
    title_en: str
    rule_score: float
    rule_confidence: str
    ai_relevance: str
    ai_initial_audit_result: str
    ai_confidence: float
    document_type_guess: str
    evidence_strength: str
    reasons: List[str]
    missing_points: List[str]
    suggested_additional_evidence: List[str]
    needs_human_review: bool
    raw_model_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ISO27001 证据分类 + AI 初步审核脚本")
    parser.add_argument("--evidence-dir", required=True, help="待分类证据目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--handbooks", nargs="*", help="审核手册 md 文件路径，不传则使用默认文件名")
    parser.add_argument("--threshold", type=float, default=base.DEFAULT_THRESHOLD, help="规则分类阈值，默认 3.5")

    parser.add_argument("--enable-ai", action="store_true", help="启用 AI 初步审核")
    parser.add_argument("--ai-provider", choices=["ollama", "deepseek", "doubao"], default="ollama", help="AI 提供方")
    parser.add_argument("--ai-model", default=None, help="模型名。DeepSeek 可用 deepseek-chat；豆包建议填你的 endpoint/model id")
    parser.add_argument("--ai-base-url", default=None, help="自定义 base_url；不传则按 provider 使用默认值")
    parser.add_argument("--ai-api-key-env", default=None, help="自定义 API Key 环境变量名")
    parser.add_argument("--ai-doc-topk", type=int, default=DEFAULT_AI_DOC_TOPK, help="每个文件最多送审多少个候选控制项，默认 3")
    parser.add_argument("--ai-min-rule-score", type=float, default=DEFAULT_AI_MIN_RULE_SCORE, help="送 AI 复核的最低规则分数，默认 4.5")
    parser.add_argument("--ai-max-context-chars", type=int, default=DEFAULT_AI_MAX_CONTEXT_CHARS, help="送给 AI 的最大上下文长度，默认 5000")
    parser.add_argument("--ai-timeout", type=int, default=DEFAULT_AI_TIMEOUT, help="AI 请求超时秒数，默认 120")
    parser.add_argument("--ai-temperature", type=float, default=0.1, help="AI 温度，默认 0.1")
    return parser.parse_args()


def provider_defaults(provider: str) -> Tuple[str, Optional[str], str]:
    if provider == "ollama":
        return "http://localhost:11434/v1/", "llama3.2:1b", "OLLAMA_API_KEY"
    if provider == "deepseek":
        return "https://api.deepseek.com", "deepseek-chat", "DEEPSEEK_API_KEY"
    return "https://ark.cn-beijing.volces.com/api/v3", None, "ARK_API_KEY"


def get_client_and_model(args: argparse.Namespace):
    if OpenAI is None:
        raise RuntimeError("未安装 openai SDK。请先执行: pip install openai")

    default_base_url, default_model, default_key_env = provider_defaults(args.ai_provider)
    base_url = args.ai_base_url or default_base_url
    model = args.ai_model or default_model
    key_env = args.ai_api_key_env or default_key_env
    api_key = os.environ.get(key_env)

    if args.ai_provider == "ollama":
        api_key = api_key or "ollama"
    elif not api_key:
        raise RuntimeError(f"缺少 API Key。请先设置环境变量 {key_env}")
    if not model:
        raise RuntimeError("当前 provider 需要显式传入 --ai-model。例如豆包/火山方舟通常需要你自己的 endpoint/model id。")

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=args.ai_timeout)
    return client, model, base_url, key_env


def safe_excerpt(text: str, max_chars: int) -> str:
    text = text.replace("\x00", " ").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.6)]
    tail = text[-int(max_chars * 0.25):]
    return head + "\n\n[...中间省略...]\n\n" + tail


def build_ai_context(doc: base.DocumentInfo, match: base.MatchResult, rules_map: Dict[str, base.Rule], max_chars: int) -> str:
    rule = rules_map[match.control_id]
    evidence_desc = "；".join(rule.required_evidence[:8]) or "无"
    core = "；".join(rule.core_keywords[:10]) or "无"
    aux = "；".join(rule.aux_keywords[:10]) or "无"
    snippets = "\n".join(f"- {s}" for s in match.snippets[:6]) or "- 无"
    matched = {
        "matched_in_name": match.matched_in_name[:8],
        "matched_domain_terms": match.matched_domain_terms[:12],
        "matched_core_keywords": match.matched_core_keywords[:12],
        "matched_aux_keywords": match.matched_aux_keywords[:12],
        "matched_required_evidence": match.matched_required_evidence[:8],
        "matched_evidence_type_terms": match.matched_evidence_type_terms[:8],
    }
    source_text = safe_excerpt(doc.text or doc.normalized_text, max_chars=max_chars)
    context = {
        "file_name": doc.file_name,
        "file_path": str(doc.path),
        "control_id": match.control_id,
        "control_title_cn": match.title_cn,
        "control_title_en": match.title_en,
        "rule_score": match.score,
        "rule_confidence": match.confidence,
        "required_evidence": evidence_desc,
        "core_keywords": core,
        "aux_keywords": aux,
        "rule_hit_summary": matched,
        "rule_snippets": snippets,
        "document_text_excerpt": source_text,
    }
    return json.dumps(context, ensure_ascii=False, indent=2)


def ai_system_prompt() -> str:
    return textwrap.dedent(
        """
        你是一名 ISO/IEC 27001 审核辅助分析员。
        你的任务不是做最终认证结论，而是根据给定控制项与证据文本，输出“初步审核意见”。

        你必须遵守：
        1. 不能把“提到过”直接等同于“已落实”。
        2. 模板、空表、历史版本、非正式草稿，不能轻易视为充分证据。
        3. 当证据不足、版本日期不清、审批信息不清、责任分工不清时，倾向给出 partial / uncertain，并标记 needs_human_review=true。
        4. 只输出 JSON，不要输出解释性散文，不要使用 markdown 代码块。

        JSON 字段必须包含：
        {
          "ai_relevance": "high|medium|low",
          "ai_initial_audit_result": "pass|partial|fail|uncertain",
          "ai_confidence": 0.0,
          "document_type_guess": "policy|procedure|record|report|log|inventory|minutes|other",
          "evidence_strength": "strong|medium|weak",
          "reasons": ["..."],
          "missing_points": ["..."],
          "suggested_additional_evidence": ["..."],
          "needs_human_review": true
        }
        """
    ).strip()


def extract_first_json(text: str) -> Dict:
    text = text.strip()
    if not text:
        raise ValueError("模型返回为空")
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("模型返回中未找到 JSON 对象")
    return json.loads(m.group(0))


def call_ai_review(client, model: str, context_json: str, temperature: float) -> Tuple[Dict, str]:
    user_prompt = (
        "请根据下面的控制项与证据上下文，输出严格 JSON。\n"
        "注意：这是初步审核，不是最终结论。\n\n"
        f"{context_json}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ai_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    content = response.choices[0].message.content or ""
    parsed = extract_first_json(content)
    return parsed, content


def normalize_ai_result(raw: Dict, match: base.MatchResult) -> Dict:
    def as_list(key: str) -> List[str]:
        val = raw.get(key, [])
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        if isinstance(val, str) and val.strip():
            return [val.strip()]
        return []

    ai_confidence = raw.get("ai_confidence", 0.0)
    try:
        ai_confidence = float(ai_confidence)
    except Exception:
        ai_confidence = 0.0
    ai_confidence = max(0.0, min(1.0, ai_confidence))

    return {
        "file_path": match.file_path,
        "control_id": match.control_id,
        "title_cn": match.title_cn,
        "title_en": match.title_en,
        "rule_score": match.score,
        "rule_confidence": match.confidence,
        "ai_relevance": str(raw.get("ai_relevance", "uncertain")).strip().lower() or "uncertain",
        "ai_initial_audit_result": str(raw.get("ai_initial_audit_result", "uncertain")).strip().lower() or "uncertain",
        "ai_confidence": ai_confidence,
        "document_type_guess": str(raw.get("document_type_guess", "other")).strip().lower() or "other",
        "evidence_strength": str(raw.get("evidence_strength", "weak")).strip().lower() or "weak",
        "reasons": as_list("reasons"),
        "missing_points": as_list("missing_points"),
        "suggested_additional_evidence": as_list("suggested_additional_evidence"),
        "needs_human_review": bool(raw.get("needs_human_review", True)),
    }


def write_ai_outputs(output_dir: Path, ai_results: List[AIAuditResult]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    detail_csv = output_dir / "ai_audit_detail.csv"
    with detail_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "file_path", "control_id", "title_cn", "title_en", "rule_score", "rule_confidence",
            "ai_relevance", "ai_initial_audit_result", "ai_confidence", "document_type_guess",
            "evidence_strength", "needs_human_review", "reasons", "missing_points", "suggested_additional_evidence",
        ])
        for r in ai_results:
            writer.writerow([
                r.file_path, r.control_id, r.title_cn, r.title_en, r.rule_score, r.rule_confidence,
                r.ai_relevance, r.ai_initial_audit_result, r.ai_confidence, r.document_type_guess,
                r.evidence_strength, r.needs_human_review,
                "；".join(r.reasons),
                "；".join(r.missing_points),
                "；".join(r.suggested_additional_evidence),
            ])

    summary_json = output_dir / "ai_audit_summary.json"
    summary_json.write_text(
        json.dumps([dataclasses.asdict(r) for r in ai_results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_md = output_dir / "ai_report.md"
    lines: List[str] = [
        "# ISO27001 AI 初步审核报告",
        "",
        f"- AI 审核条目数：{len(ai_results)}",
        "- 说明：以下为 AI 初步审核意见，不能替代人工最终结论。",
        "",
    ]
    for r in ai_results:
        lines.append(f"## {Path(r.file_path).name} -> {r.control_id} {r.title_cn or r.title_en}")
        lines.append("")
        lines.append(f"- 规则分数：{r.rule_score}（{r.rule_confidence}）")
        lines.append(f"- AI 相关性：{r.ai_relevance}")
        lines.append(f"- 初步审核结果：{r.ai_initial_audit_result}")
        lines.append(f"- AI 置信度：{r.ai_confidence}")
        lines.append(f"- 文档类型猜测：{r.document_type_guess}")
        lines.append(f"- 证据强度：{r.evidence_strength}")
        lines.append(f"- 需要人工复核：{r.needs_human_review}")
        if r.reasons:
            lines.append("- 原因：")
            for item in r.reasons:
                lines.append(f"  - {item}")
        if r.missing_points:
            lines.append("- 缺口：")
            for item in r.missing_points:
                lines.append(f"  - {item}")
        if r.suggested_additional_evidence:
            lines.append("- 建议补证：")
            for item in r.suggested_additional_evidence:
                lines.append(f"  - {item}")
        lines.append("")
    report_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    evidence_dir = Path(args.evidence_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not evidence_dir.exists():
        print(f"[错误] 证据目录不存在：{evidence_dir}", file=sys.stderr)
        sys.exit(1)

    handbook_paths = [Path(p).resolve() for p in args.handbooks] if args.handbooks else base.default_handbook_paths(script_dir)
    rules = base.load_rules_from_handbooks(handbook_paths)
    if not rules:
        print("[错误] 未从手册中解析出任何规则。", file=sys.stderr)
        sys.exit(1)

    df_map = base.compute_keyword_df(rules)
    docs = [base.read_document(p) for p in base.iter_evidence_files(evidence_dir)]

    all_results: Dict[str, List[base.MatchResult]] = {}
    for doc in docs:
        all_results[str(doc.path)] = base.classify_document(doc, rules, df_map, args.threshold)

    base.write_results(output_dir, rules, docs, all_results)
    classified = sum(1 for v in all_results.values() if v)
    print(f"[完成-规则分类] 共处理 {len(docs)} 个文件，命中分类 {classified} 个文件。")

    if not args.enable_ai:
        print("[提示] 未启用 AI 初审。规则结果已输出。")
        print(f"[输出目录] {output_dir}")
        return

    client, model, base_url, key_env = get_client_and_model(args)
    print(f"[AI] provider={args.ai_provider} base_url={base_url} model={model} key_env={key_env}")

    rules_map = {r.control_id: r for r in rules}
    docs_map = {str(d.path): d for d in docs}

    ai_results: List[AIAuditResult] = []
    for file_path, matches in all_results.items():
        if not matches:
            continue
        shortlisted = [m for m in matches if m.score >= args.ai_min_rule_score][: args.ai_doc_topk]
        for m in shortlisted:
            doc = docs_map[file_path]
            context_json = build_ai_context(doc, m, rules_map, args.ai_max_context_chars)
            try:
                parsed, raw_text = call_ai_review(client, model, context_json, args.ai_temperature)
                normalized = normalize_ai_result(parsed, m)
                ai_results.append(
                    AIAuditResult(raw_model_text=raw_text, **normalized)
                )
                print(f"[AI OK] {Path(file_path).name} -> {m.control_id} {normalized['ai_initial_audit_result']}")
            except Exception as e:
                ai_results.append(
                    AIAuditResult(
                        file_path=m.file_path,
                        control_id=m.control_id,
                        title_cn=m.title_cn,
                        title_en=m.title_en,
                        rule_score=m.score,
                        rule_confidence=m.confidence,
                        ai_relevance="error",
                        ai_initial_audit_result="uncertain",
                        ai_confidence=0.0,
                        document_type_guess="other",
                        evidence_strength="weak",
                        reasons=[f"AI 调用失败：{e}"],
                        missing_points=[],
                        suggested_additional_evidence=[],
                        needs_human_review=True,
                        raw_model_text="",
                    )
                )
                print(f"[AI ERR] {Path(file_path).name} -> {m.control_id}: {e}")

    write_ai_outputs(output_dir, ai_results)
    print(f"[完成-AI 初审] 共输出 {len(ai_results)} 条 AI 初审记录。")
    print(f"[输出目录] {output_dir}")
    print("已生成：classification_detail.csv / classification_summary.json / classification_by_control.csv / compiled_rules.csv / report.md / ai_audit_detail.csv / ai_audit_summary.json / ai_report.md")


if __name__ == "__main__":
    main()
