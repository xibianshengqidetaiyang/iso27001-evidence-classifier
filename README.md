# ISO27001 Evidence Classifier

一个面向 ISO/IEC 27001 审核证据初筛、控制项多对多映射与 AI 初步审核的辅助工具 Demo。

## 项目定位
本项目用于解决 ISO27001 审核场景中的三类问题：
1. 证据命名不统一，单靠文件名难以归档
2. 同一份证据可能对应多个控制项
3. 人工逐份初筛效率低，且容易漏掉“部分相关但证据不足”的材料

## 核心流程
文本提取 → 规则初筛 → 多对多映射 → AI 初步审核 → 人工复核

## 流程图

```mermaid
flowchart LR
    A[证据文件] --> B[文本提取]
    B --> C[规则初筛]
    C --> D[候选控制项聚合]
    D --> E[AI 初步审核]
    E --> F[结构化输出]
    F --> G[人工复核]
```

## 适用边界
- 适合：审核前归档、初筛、缺口提示、补证建议、脱敏 Demo 展示
- 不适合：直接替代人工审计结论、直接作为最终认证判定依据

## 仓库亮点
- 规则分类版
- 云端 AI 初步审核版
- 本地 Ollama 初步审核版
- sample_evidence / sample_output 脱敏样例
- docs 文档说明
---

## 项目能力

### 1) 规则分类版
- 支持 **多对多** 证据分类
- 同时分析 **文件名 + 文本内容**
- 可从结构化审核手册中抽取规则
- 输出命中原因、关键词、分数、置信度
- 适合做证据归档、初筛和规则库雏形

### 2) 云端 AI 初步审核版
- 在规则分类后，仅对高相关候选项做 AI 复核
- 支持 **DeepSeek / 豆包 / 火山方舟** 等 OpenAI 兼容接口
- 输出结构化审核意见，例如：
  - `ai_relevance`
  - `ai_initial_audit_result`
  - `ai_confidence`
  - `document_type_guess`
  - `evidence_strength`
  - `missing_points`
  - `suggested_additional_evidence`
  - `needs_human_review`

### 3) 本地模型初步审核版
- 支持通过 **Ollama** 调用本地模型
- 适合真实证据不方便上传外网的场景
- 保持与云端 AI 版相似的输出结构
- 更适合做脱敏演示、本地验证和安全场景实验

---

## 适用场景

本项目适合用于以下场景：

- ISO27001 审核前的证据归档和初筛
- 证据与控制项的多对多映射
- 审核手册规则库雏形验证
- AI 辅助的初步审核、缺口识别、补证建议
- 管理评审、内部审核、不符合项等材料的结构化整理

---

## 项目结构

```text
iso27001-evidence-classifier/
├─ iso27001_evidence_classifier.py            # 规则分类版
├─ iso27001_evidence_classifier_ai.py         # 云端 AI 初步审核版
├─ iso27001_evidence_classifier_ai_local.py   # 本地 Ollama 初步审核版
├─ requirements.txt
├─ README.md
├─ AI_UPGRADE.md
├─ docs/
├─ sample_evidence/                           # 脱敏示例输入
└─ sample_output/                             # 脱敏示例输出
