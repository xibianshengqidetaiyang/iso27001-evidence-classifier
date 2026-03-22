# ISO27001 Evidence Classifier

一个面向 **ISO/IEC 27001 审核证据初筛与归档** 的多对多分类脚本。

它不是只看文件名，而是会同时分析 **文件名 + 文本内容**，把一个证据映射到多个控制项；同一个控制项也可以匹配多个证据。

## 项目特点

- 支持 **多对多** 分类
- 同时看 **文件名与正文内容**
- 可从结构化审核手册中自动抽取规则
- 输出 **命中原因、关键词、片段、分数、置信度**
- 适合做 **审核前资料归档、规则库雏形、AI/脚本辅助审核**

## 支持格式

- `.md`
- `.txt`
- `.docx`
- `.pdf`（需可提取文本）
- `.xlsx`
- `.csv`
- `.json`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 基本用法

```bash
python iso27001_evidence_classifier.py \
  --evidence-dir ./evidence \
  --output-dir ./output \
  --handbooks ./handbooks/ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md ./handbooks/ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md
```

## Windows PowerShell 示例

```powershell
python ".\iso27001_evidence_classifier.py" `
  --evidence-dir ".\evidence" `
  --output-dir ".\output" `
  --handbooks `
  ".\handbooks\ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md" `
  ".\handbooks\ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md"
```

## 输出文件

- `classification_detail.csv`：逐文件、逐控制项命中明细
- `classification_summary.json`：按文件汇总的 Top 结果
- `classification_by_control.csv`：按控制项聚合证据
- `compiled_rules.csv`：从手册抽取出的规则
- `report.md`：简要报告

## 目录建议

```text
iso27001-evidence-classifier/
├─ iso27001_evidence_classifier.py
├─ requirements.txt
├─ README.md
├─ docs/
│  └─ manual_zh.md
├─ sample_evidence/
├─ sample_output/
└─ handbooks/
```

## 适用边界

这版更适合做 **证据分类/初筛**，不直接替代人工审核。当前不含 OCR，对扫描版 PDF、图片类文件支持有限。

## 面试怎么讲

你可以把它描述成：

> 结合 ISO27001 审核手册，独立实现了一个多对多证据分类脚本。脚本会基于文件名和正文内容自动抽取证据与控制项之间的映射关系，并输出命中原因、关键词和置信度，用于审核前资料归档和规则化沉淀。

## 重要提醒

请只上传 **脱敏后的示例文件**。不要把真实客户名称、真实日志、内部制度原文、会议纪要、审核结论等敏感资料公开到 GitHub。
