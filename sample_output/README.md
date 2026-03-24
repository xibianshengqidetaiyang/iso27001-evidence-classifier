# sample_output

这里可以放脱敏后的脚本输出示例，例如：
- classification_detail.csv（删掉真实路径和客户名）
- classification_by_control.csv（删掉真实文件名）
- report.md（仅保留演示性的统计结论）

## Current Status

This project currently supports:

- Rule-based ISO27001 audit evidence classification
- Many-to-many mapping between evidence files and control items
- Local AI preliminary audit using Ollama-compatible models
- Structured outputs in CSV / JSON / Markdown
- Human-review-oriented results such as partial match, uncertain match, and suggested additional evidence

## Demo Outputs

Anonymized sample outputs are available in:

- `sample_output/ai_demo/ai_report_demo.md`
- `sample_output/ai_demo/ai_audit_detail_demo.csv`
- `sample_output/ai_demo/ai_audit_summary_demo.json`

These demo files show how the project produces:

- candidate control mappings
- preliminary audit results
- missing evidence hints
- suggested additional evidence
- human review recommendations

## Privacy and Data Handling

This repository does **not** contain real customer evidence, raw audit records, or sensitive internal materials.

Only anonymized demo files are included.

Sensitive information is removed or replaced, including but not limited to:

- organization names
- personal names
- emails and phone numbers
- IP addresses and hostnames
- internal system names
- exact meeting records and raw evidence excerpts

## Validation

The workflow has been tested on a small batch of ISMS audit-related sample evidence, including:

- internal audit plan
- internal audit report
- nonconformity report
- management review plan
- management review improvement and verification form

The rule-based stage successfully classified all 5 test files, and the local AI stage generated preliminary audit records for the candidate controls.