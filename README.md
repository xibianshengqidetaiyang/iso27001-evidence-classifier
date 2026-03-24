# ISO27001 Evidence Classifier

一个面向 **ISO/IEC 27001 审核证据初筛、归档与 AI 初步审核** 的工具项目。

它不是只看文件名，而是会同时分析 **文件名 + 文本内容**，将一个证据映射到多个控制项；同一个控制项也可以匹配多个证据。在规则分类基础上，还支持接入 **DeepSeek / 豆包** 做 **AI 初步审核**。

## 项目能力

### 1) 规则分类版
- 支持 **多对多** 证据分类
- 同时看 **文件名与正文内容**
- 可从结构化审核手册中自动抽取规则
- 输出 **命中原因、关键词、片段、分数、置信度**
- 适合做 **审核前资料归档、规则库雏形、证据初筛**

### 2) AI 初步审核版
- 在规则分类后，仅对高相关候选项做 AI 复核
- 支持 **DeepSeek** 与 **豆包**（OpenAI 兼容接口）
- 输出结构化审核意见：
  - `ai_relevance`
  - `ai_initial_audit_result`
  - `ai_confidence`
  - `document_type_guess`
  - `evidence_strength`
  - `missing_points`
  - `suggested_additional_evidence`
  - `needs_human_review`
- 定位是 **审核辅助工具**，不是最终审计裁决工具

## 支持格式

- `.md`
- `.txt`
- `.docx`
- `.pdf`（需可提取文本）
- `.xlsx`
- `.csv`
- `.json`

## 项目结构

```text
iso27001-evidence-classifier/
├─ iso27001_evidence_classifier.py          # 规则分类版
├─ iso27001_evidence_classifier_ai.py       # AI 初步审核增强版
├─ requirements.txt
├─ README.md
├─ AI_UPGRADE.md
├─ docs/
│  └─ manual_zh.md
├─ sample_evidence/
├─ sample_output/
└─ handbooks/
```

## 安装依赖

```bash
pip install -r requirements.txt
```

如果只想跑 AI 版，也可以确保至少安装：

```bash
pip install openai python-docx pypdf openpyxl
```

## 基本用法（规则分类版）

```bash
python iso27001_evidence_classifier.py \
  --evidence-dir ./evidence \
  --output-dir ./output \
  --handbooks ./handbooks/ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md ./handbooks/ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md
```

## AI 初步审核版用法

### DeepSeek
先设置环境变量：

#### PowerShell
```powershell
$env:DEEPSEEK_API_KEY="你的key"
```

#### CMD
```cmd
set DEEPSEEK_API_KEY=你的key
```

运行：

```bash
python iso27001_evidence_classifier_ai.py \
  --evidence-dir ./evidence \
  --output-dir ./output_ai \
  --handbooks ./handbooks/ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md ./handbooks/ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md \
  --enable-ai \
  --ai-provider deepseek \
  --ai-model deepseek-chat
```

### 豆包 / 火山方舟
先设置环境变量：

#### PowerShell
```powershell
$env:ARK_API_KEY="你的key"
```

#### CMD
```cmd
set ARK_API_KEY=你的key
```

然后传入你控制台实际可用的模型或 endpoint id：

```bash
python iso27001_evidence_classifier_ai.py \
  --evidence-dir ./evidence \
  --output-dir ./output_ai \
  --handbooks ./handbooks/ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md ./handbooks/ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md \
  --enable-ai \
  --ai-provider doubao \
  --ai-model 这里填你的endpoint或model-id
```

## 输出文件

### 规则分类版输出
- `classification_detail.csv`：逐文件、逐控制项命中明细
- `classification_summary.json`：按文件汇总的 Top 结果
- `classification_by_control.csv`：按控制项聚合证据
- `compiled_rules.csv`：从手册抽取出的规则
- `report.md`：简要报告

### AI 初步审核版新增输出
- `ai_audit_detail.csv`
- `ai_audit_summary.json`
- `ai_report.md`

## 适用边界

这版更适合做 **证据分类 / 初筛 / AI 初步审核**，不直接替代人工审核。

当前限制：
- 默认不含 OCR，对扫描版 PDF、图片类文件支持有限
- AI 可能把“提到过”误判成“已落实”，因此必须保留人工复核
- 模板、空表、历史版本、草稿，不应直接视为充分证据
