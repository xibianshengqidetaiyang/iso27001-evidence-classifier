# 给 GitHub 仓库升级 AI 初步审核版：最短路径

## 你现在要做的文件改动
把下面两个文件放进你本地仓库目录：

- `iso27001_evidence_classifier_ai.py`
- 这份说明文档（可选）

另外，把 `requirements.txt` 追加一行：

```txt
openai>=1.0.0
```

## 运行前先装依赖

```bash
pip install -r requirements.txt
```

如果你不想改 `requirements.txt`，也可以直接：

```bash
pip install openai
```

## DeepSeek 用法
先设置环境变量：

### CMD
```cmd
set DEEPSEEK_API_KEY=你的key
```

### PowerShell
```powershell
$env:DEEPSEEK_API_KEY="你的key"
```

运行：

```bash
python iso27001_evidence_classifier_ai.py ^
  --evidence-dir .\evidence ^
  --output-dir .\output_ai ^
  --handbooks ^
  ".\ISO27001_2022_审核手册与模板_交付包\ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md" ^
  ".\ISO27001_2022_附录A_A5-A8_审核手册与规则库_交付包\ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md" ^
  --enable-ai ^
  --ai-provider deepseek ^
  --ai-model deepseek-chat
```

## 豆包 / 火山方舟用法
先设置环境变量：

### CMD
```cmd
set ARK_API_KEY=你的key
```

### PowerShell
```powershell
$env:ARK_API_KEY="你的key"
```

然后传入你在方舟控制台实际可用的 `endpoint/model id`：

```bash
python iso27001_evidence_classifier_ai.py ^
  --evidence-dir .\evidence ^
  --output-dir .\output_ai ^
  --handbooks ^
  ".\ISO27001_2022_审核手册与模板_交付包\ISO27001_2022_信息安全管理体系总则审核手册_V1.0.md" ^
  ".\ISO27001_2022_附录A_A5-A8_审核手册与规则库_交付包\ISO27001_2022_附录A_A5-A8_控制项审核手册_V1.0.md" ^
  --enable-ai ^
  --ai-provider doubao ^
  --ai-model 这里填你的endpoint或model-id
```

## 输出文件
除了原来的规则分类输出，还会新增：

- `ai_audit_detail.csv`
- `ai_audit_summary.json`
- `ai_report.md`

## 推到 GitHub
你本地仓库目录里执行：

```bash
git add .
git commit -m "Add AI preliminary audit support"
git push origin master
```

如果你以后把默认分支改成 `main`，最后一条就改成：

```bash
git push origin main
```
