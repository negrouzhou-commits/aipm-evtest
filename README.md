# aipm-evtest

对 AI 产品经理的能力模型进行测评。

一个 WorkBuddy / Claude Skill：以**交互式问答**的方式测评 AI 产品经理能力——逐题提问、逐题评分点评，全部答完后生成一份结构化测评报告。

## 能力模型与题库来源

| 内容 | 来源 |
|------|------|
| 五维能力模型（技术认知 / 产品基本功 / 数据与评估 / 商业判断 / 伦理与合规）与「熟悉大模型」L1-L3 档位 | 《AI 产品经理能力模型》（基于公开 AI PM 招聘 JD 整理） |
| 题库原素材（94 道英文面试题） | awesome-generative-ai-guide · `interview_prep/roles/ai-product-manager` |

题库已精选改编为 **50 道中文题**（五维 × 基础/进阶/挑战各 10 题），每题配「及格要点 / 优秀要点」作为评分锚点。

## 安装

克隆到用户级技能目录即可使用：

```bash
git clone git@github.com:negrouzhou-commits/aipm-evtest.git ~/.workbuddy/skills/ai-pm-assessment
```

## 使用

在 WorkBuddy 中直接说：

- 「测一下我的 AI PM 能力」
- 「我想做 AI 产品经理能力测评」
- 「AI PM 能力摸底」

默认 **10 题**（五维各 2 题，约 20-30 分钟），一次只问一题，答完给分和点评，结束后生成 Markdown 报告。

### 测评流程

```
开场确认（姓名 / 背景 / 题量）
        ↓
五维度各 2 题，难度自适应
  ├─ 第 1 题：基础档
  └─ 第 2 题：上题 ≥4 分 → 挑战档；=3 → 进阶档；≤2 → 基础档换一题
        ↓
对话内口语化总结 + 生成 Markdown 测评报告
```

### 报告包含

综合得分、五维得分与档位、大模型熟悉度 L1/L2/L3 定档、短板优先级排序、逐题明细、2-4 周内可验证的提升计划、评分标准附录。

## 目录结构

```
.
├── SKILL.md                        # 技能主文件（流程与评分规则）
├── references/
│   ├── capability-model.md         # 评分尺子：及格线/优秀线、1-5 分标准、L 档位定档算法、提升建议库
│   └── question-bank.md            # 50 道题库（题干 + 及格要点 + 优秀要点）
├── scripts/
│   └── generate_report.py          # 由打分 JSON 生成 Markdown 报告（纯标准库）
└── assets/
    └── report-template.md          # 报告版式模板
```

## 单独使用报告生成脚本

不跑完整测评，只想把已有打分数据生成报告：

```bash
python3 scripts/generate_report.py scores.json -o 报告.md
```

`scores.json` 格式：

```json
{
  "name": "姓名",
  "date": "2026-10-26",
  "context": "3 年传统 PM，正在转 AI PM",
  "questions": [
    {"id": "T01", "dimension": "技术认知", "difficulty": "基础",
     "stem": "题干摘要", "score": 4, "note": "答到 X，漏掉 Y"}
  ]
}
```

`dimension` 必须是五个维度之一；可选 `diagnoses` 字段覆盖某维度的默认诊断文案。

## 评分口径

- **单题 1-5 分**：1 明显不足 · 2 接近及格 · 3 及格 · 4 良好（及格要点全覆盖 + 至少 1 个优秀要点） · 5 优秀
- **维度得分** = 该维度题目平均分；**综合得分** = 五维平均分（等权）
- **档位**：`<2.5` 未达及格线 · `2.5–3.4` 及格线附近 · `3.5–4.4` 及格与优秀之间 · `≥4.5` 优秀线以上
- **L 档位**：技术认知 `<2.5` → 未达 L1；`2.5–3.4` → L1；`3.5–4.4` → L2；`≥4.5` 且商业判断 `≥4.0` → L3；`≥4.5` 但商业判断 `<4.0` → L2+

详见 `references/capability-model.md`。

## 许可

本项目采用 [MIT License](LICENSE)。

`references/question-bank.md` 中约 40 道题改编自 [awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide)（MIT License, Copyright 2024 Aishwarya Naresh Reganti），第三方声明见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。
