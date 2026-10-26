#!/usr/bin/env python3
"""
从测评打分数据生成《AI 产品经理能力测评报告》Markdown 文件。

用法:
    python3 generate_report.py <scores.json> [-o 输出路径]

scores.json 格式:
{
  "name": "被测评者姓名",
  "date": "2026-10-26",                      // 可选，默认今天
  "context": "3 年传统 PM，正在转 AI PM",      // 可选
  "questions": [
    {
      "id": "T04",                            // 题库编号
      "dimension": "技术认知",                 // 五维度之一
      "difficulty": "进阶",                    // 基础 / 进阶 / 挑战
      "stem": "题干（可截断）",
      "score": 4,                             // 1-5
      "note": "点评：答到的点 / 漏掉的点"       // 可选
    }
  ],
  "diagnoses": { "技术认知": "自定义诊断文案" }  // 可选，覆盖默认诊断
}

只依赖标准库。评分规则见 ../references/capability-model.md。
"""

import argparse
import json
import os
import sys
from datetime import date

DIMENSIONS = ["技术认知", "产品基本功", "数据与评估", "商业判断", "伦理与合规"]

# 短板同分时的优先补顺序：越靠前越优先
GAP_PRIORITY = ["数据与评估", "技术认知", "商业判断", "伦理与合规", "产品基本功"]

LEVEL_DESC = {
    "未达 L1": "L0 · 概念层有缺口",
    "L1": "L1 · 概念可用",
    "L2": "L2 · 方案可判",
    "L2+": "L2+ · 接近 L3（成本/取舍证据不足）",
    "L3": "L3 · 选型可辩",
}

LEVEL_MEANING = {
    "未达 L1": "能说清大模型擅长什么、不擅长什么；知道 token、上下文窗口、温度对体验的含义；亲手调过 1-2 个主流 API。",
    "L1": "能说清大模型擅长什么、不擅长什么；知道 token、上下文窗口、温度对体验的含义；亲手调过 1-2 个主流 API。",
    "L2": "能用 PM 语言讲清模型机制对长文本、延迟、成本的工程含义；面对具体场景能在 Prompt / RAG / 微调 / Agent 之间给出有依据的初判。",
    "L2+": "技术判断已达 L3 水平，但成本、延迟、合规的取舍证据还不够硬，需要补上「凭什么这么选」的量化依据。",
    "L3": "业务目标扔过来能倒推约束（效果底线、延迟、成本、合规），与算法平等讨论候选方案与取舍；解释「为什么不用大模型」同样有依据。",
}

# 每个维度 × 三档的提升动作（2-4 周内可验证）
PLAN = {
    "技术认知": {
        "low": [
            "读完一份主流模型 API 文档，亲手调通 1-2 个调用。",
            "整理一页「大模型能力边界清单」：擅长什么、不擅长什么、典型失败模式。",
        ],
        "mid": [
            "选一个真实工作场景，写一页「方案选型备忘」：目标、失败可接受度、候选路径（Prompt / RAG / 微调 / 不上 AI）、放弃理由。",
            "用 10-20 条样本做一次最小对照实验，用数据而不是会议拍板。",
        ],
        "high": [
            "参与或旁听一次真实选型会，会后写清「约束 / 候选 / 取舍 / 复盘」四栏。",
            "补一份粗算的 token 成本与延迟预算，主动拿去被人挑战。",
        ],
    },
    "产品基本功": {
        "low": [
            "把最近一份 PRD 改写成「概率性 PRD」：补上允许的错误率、失败模式清单、每种失败的兜底路径、成本与延迟预算。",
        ],
        "mid": [
            "为一个 AI 功能画「自主权阶梯」（只读告知 → 建议 → 起草 → 执行），给每个动作标注可逆性、错误代价、确认机制。",
            "练「一页纸讲清 AI 功能」：目标用户 / 核心场景 / 成功标准 / 明确不做的事。",
        ],
        "high": [
            "对一个已上线 AI 功能做完整复盘：成功标准是否先验、护栏指标是否真的报警、失败路径是否被用到。",
            "把「什么时候该拒绝上 AI」写成一条团队可复用的判据，并在下一次需求评审里实际用一次。",
        ],
    },
    "数据与评估": {
        "low": [
            "从零建一个 20-50 条的最小评测集：自己写用例和判定标准，覆盖常见案例 + 你最怕的边界案例。",
            "搞清楚自己产品该分开看哪两个半程指标（如检索 recall@k 与生成 faithfulness）。",
        ],
        "mid": [
            "跑一次完整 badcase 闭环：收集 30 条线上失败样本，人工读一遍，聚类成失败模式，按占比排序。",
            "把 Top 失败模式写进评测集并定指标，形成「收集—归因—分发—验证」的常态流程。",
        ],
        "high": [
            "搭一个 LLM-as-a-Judge，用 100 条人工标注验证它：算一致率，查位置偏见与冗长偏见。",
            "建立「离线指标 vs 线上指标」背离告警，并做一次评测集轮换防止过拟合。",
        ],
    },
    "商业判断": {
        "low": [
            "给手上一个 AI 功能算一笔账：单次调用输入输出 token 量 × 单价 × 日调用量 = 月度成本，再除以 MAU 得人均成本。",
        ],
        "mid": [
            "写一份「自建 / 微调 vs 调 API」决策备忘，覆盖效果、成本、延迟、数据护城河、供应商锁定风险、退出路径六个维度。",
        ],
        "high": [
            "设计一套分级路由 / 缓存 / 输出长度封顶的降本方案，给出预估降本比例与质量损失上限。",
            "算出毛利率对用量和模型单价的敏感点，写成一页给老板看的单位经济模型。",
        ],
    },
    "伦理与合规": {
        "low": [
            "列出自己产品适用的国内监管要求清单，标出每条对应的产品动作。",
            "查清公司内部法务 / 安全团队的对接人和升级路径，写成一页备忘。",
        ],
        "mid": [
            "做一次红队测试：准备 20-30 条对抗性输入（越狱、提示词注入、越界请求、敏感话题），跑一遍并记录失败。",
            "把所有失败永久加入评测集，并给不可逆动作补上人工确认与审计日志。",
        ],
        "high": [
            "把公平、隐私、透明写成 PRD 的验收标准：分人群评测切片与阈值、数据最小化与留存、AI 参与披露。",
            "建一套上线前合规门禁清单，并明确自己产品的风险分级与对应义务。",
        ],
    },
}


def tier_of(score: float) -> str:
    if score < 2.5:
        return "未达及格线"
    if score < 3.5:
        return "及格线附近"
    if score < 4.5:
        return "及格与优秀之间"
    return "优秀线以上"


def plan_tier_of(score: float) -> str:
    if score < 3.5:
        return "low"
    if score < 4.5:
        return "mid"
    return "high"


def decide_level(t: float, e: float, b: float) -> tuple:
    """返回 (档位 key, 定档说明列表)。"""
    notes = []
    if t < 2.5:
        level = "未达 L1"
    elif t < 3.5:
        level = "L1"
    elif t < 4.5:
        level = "L2"
    else:
        if b >= 4.0:
            level = "L3"
        else:
            level = "L2+"
            notes.append(
                f"技术认知已达 {t:.1f}（≥4.5），但商业判断仅 {b:.1f}（<4.0）——"
                "方案判断够了，成本与取舍的量化证据还不够，差一口气到 L3。"
            )
    if e < 2.5:
        notes.append(
            f"数据与评估仅 {e:.1f}（<2.5）：即便方案判断到位，也缺少评测证据支撑，"
            "选型结论在面试或评审中容易站不住。建议与 L 档位同步补。"
        )
    return level, notes


def default_diagnosis(dim: str, score: float) -> str:
    tier = tier_of(score)
    base = {
        "技术认知": {
            "未达及格线": "方案层判断尚未成型，容易被算法结论带着走，需要先补能力边界与选型判据。",
            "及格线附近": "概念层过关，但从「知道是什么」到「能判断该不该用、用哪种」还有明显距离。",
            "及格与优秀之间": "能做初步方案判断，缺的是把判断落成可辩护的约束与证据。",
            "优秀线以上": "能在早期参与技术选型，并能把「不适合用模型」同样讲出依据。",
        },
        "产品基本功": {
            "未达及格线": "传统 PM 基本功尚未迁移到概率性系统，PRD 里缺少错误率与兜底设计。",
            "及格线附近": "基本功扎实，但还没翻译成 AI 场景的语言（错误容忍度、分流机制）。",
            "及格与优秀之间": "能翻译基本功能，但自主权、错误代价这类 AI 特有的设计还不够系统。",
            "优秀线以上": "能把确定性产品方法论完整迁移到概率性系统，并明确划出「不做」的边界。",
        },
        "数据与评估": {
            "未达及格线": "缺少评测集意识，「效果好」还没有可度量的定义，这是最需要优先补的一块。",
            "及格线附近": "知道要有评测集，但还没跑通过完整的 badcase 归因闭环。",
            "及格与优秀之间": "能搭评测集并做归因，缺的是自动化裁判与线上线下背离的告警机制。",
            "优秀线以上": "评测体系完整，能区分模型指标与业务指标并解释二者的脱节。",
        },
        "商业判断": {
            "未达及格线": "对 AI 的边际成本结构尚无体感，容易做出不可持续的定价或功能承诺。",
            "及格线附近": "知道成本是变量，但还没算过自己产品的单位经济账。",
            "及格与优秀之间": "能算账、能做选型取舍，缺的是降本方案设计与定价策略的主动权。",
            "优秀线以上": "能主导选型决策框架与降本方案，并把成本放进商业化策略。",
        },
        "伦理与合规": {
            "未达及格线": "风险边界模糊，遇到红线可能自己拍板而不是升级，这是合规事故的高发区。",
            "及格线附近": "知道有哪些风险和该找谁，但还没在设计阶段主动做缓解。",
            "及格与优秀之间": "能在设计阶段识别风险，缺的是红队测试与成体系的合规门禁。",
            "优秀线以上": "能把公平、隐私、透明写成验收标准，并按风险分级管理上线决策。",
        },
    }
    return base[dim][tier]


def build_dim_table(scores: dict, diagnoses: dict) -> str:
    lines = ["| 维度 | 得分 | 档位 | 诊断 |", "|------|------|------|------|"]
    for dim in DIMENSIONS:
        s = scores[dim]
        lines.append(
            f"| {dim} | {s:.1f} / 5.0 | {tier_of(s)} | {diagnoses[dim]} |"
        )
    return "\n".join(lines)


def build_detail_table(questions: list) -> str:
    lines = ["| # | 维度 | 难度 | 题目 | 得分 | 点评 |", "|---|------|------|------|------|------|"]
    for i, q in enumerate(questions, 1):
        stem = q.get("stem", "").replace("|", "／").replace("\n", " ")
        if len(stem) > 42:
            stem = stem[:42] + "…"
        note = q.get("note", "").replace("|", "／").replace("\n", " ") or "—"
        lines.append(
            f"| {i} | {q['dimension']} | {q.get('difficulty', '—')} | {stem} | "
            f"{q['score']} / 5 | {note} |"
        )
    return "\n".join(lines)


def build_gaps(scores: dict) -> str:
    ranked = sorted(DIMENSIONS, key=lambda d: (scores[d], GAP_PRIORITY.index(d)))
    lines = []
    for i, dim in enumerate(ranked, 1):
        s = scores[dim]
        if s >= 4.5:
            tag = "**优势项，保持并做成可演示的判断证据**"
        elif s >= 3.5:
            tag = "次要改进项"
        elif s >= 2.5:
            tag = "**优先补**"
        else:
            tag = "**最优先补（短板）**"
        lines.append(f"{i}. **{dim}** — {s:.1f} 分（{tier_of(s)}） · {tag}")
    top2 = ranked[:2]
    lines.append(
        f"\n接下来 2-4 周把精力集中在 **{top2[0]}**"
        + (f" 和 **{top2[1]}**" if len(top2) > 1 else "")
        + "，其余维度维持即可。"
    )
    return "\n".join(lines)


def build_plan(scores: dict) -> str:
    ranked = sorted(DIMENSIONS, key=lambda d: (scores[d], GAP_PRIORITY.index(d)))
    blocks = []
    for dim in ranked:
        s = scores[dim]
        tier_key = plan_tier_of(s)
        actions = PLAN[dim][tier_key]
        blocks.append(f"### {dim} · {s:.1f} 分（{tier_of(s)}）\n")
        blocks.extend(f"- [ ] {a}" for a in actions)
        blocks.append("")
    return "\n".join(blocks).strip()


def build_overall(total: float, level: str, scores: dict) -> str:
    ranked = sorted(DIMENSIONS, key=lambda d: (scores[d], GAP_PRIORITY.index(d)))
    if total >= 4.5:
        head = "整体已达优秀线，具备主导 AI 产品全流程决策的能力。"
    elif total >= 3.5:
        head = "整体处于及格与优秀之间，主干能力成型，短板集中在少数几个维度。"
    elif total >= 2.5:
        head = "整体刚过及格线，能上手 AI 产品工作，但关键判断还依赖他人的结论。"
    else:
        head = "整体尚未达到 AI PM 的及格线，需要先补齐基础概念与评测方法论。"
    return (
        f"{head}综合得分 **{total:.1f} / 5.0**，大模型熟悉度定档 **{LEVEL_DESC[level]}**。\n\n"
        f"最强维度：**{ranked[-1]}**（{scores[ranked[-1]]:.1f}）；"
        f"最短维度：**{ranked[0]}**（{scores[ranked[0]]:.1f}）。"
    )


def build_appendix() -> str:
    return (
        "- **单题 1-5 分**：1 明显不足（概念错误 / 只背术语 / 空答）｜2 接近及格（方向对但缺关键约束）｜"
        "3 及格（命中该维度及格线要点）｜4 良好（及格要点全覆盖 + 至少 1 个优秀要点）｜"
        "5 优秀（及格与优秀要点全覆盖，能落到场景、指标、决策证据）。\n"
        "- **维度得分** = 该维度题目平均分；**综合得分** = 五维平均分（等权）。\n"
        "- **档位**：<2.5 未达及格线｜2.5–3.4 及格线附近｜3.5–4.4 及格与优秀之间｜≥4.5 优秀线以上。\n"
        "- **L 档位算法**：技术认知 <2.5 → 未达 L1；2.5–3.4 → L1；3.5–4.4 → L2；"
        "≥4.5 且商业判断 ≥4.0 → L3；≥4.5 但商业判断 <4.0 → L2+。"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="生成 AI PM 能力测评报告")
    ap.add_argument("scores", help="打分 JSON 文件路径")
    ap.add_argument("-o", "--output", help="输出 Markdown 路径（默认与 JSON 同目录）")
    args = ap.parse_args()

    with open(args.scores, encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    if not questions:
        print("错误：questions 为空。", file=sys.stderr)
        return 1

    buckets = {d: [] for d in DIMENSIONS}
    for q in questions:
        dim = q.get("dimension")
        if dim not in buckets:
            print(f"错误：未知维度 {dim!r}，应为 {DIMENSIONS} 之一。", file=sys.stderr)
            return 1
        buckets[dim].append(q["score"])

    scores = {d: (sum(v) / len(v) if v else 0.0) for d, v in buckets.items()}
    total = sum(scores.values()) / len(DIMENSIONS)

    custom = data.get("diagnoses", {})
    diagnoses = {d: custom.get(d, default_diagnosis(d, scores[d])) for d in DIMENSIONS}

    level, notes = decide_level(scores["技术认知"], scores["数据与评估"], scores["商业判断"])
    level_basis = [
        f"- 判定口径：技术认知 {scores['技术认知']:.1f}、商业判断 {scores['商业判断']:.1f}、"
        f"数据与评估 {scores['数据与评估']:.1f}。",
        f"- 该档位意味着：{LEVEL_MEANING[level]}",
    ]
    level_basis += [f"- {n}" for n in notes]
    if scores["伦理与合规"] < 2.5:
        level_basis.append(
            f"- ⚠️ 风险提示：伦理与合规仅 {scores['伦理与合规']:.1f}（<2.5），"
            "虽不影响 L 档位，但属于合规事故高发区，建议尽快补监管清单与升级路径。"
        )

    per_dim = "、".join(f"{d} {len(buckets[d])} 题" for d in DIMENSIONS if buckets[d])

    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "report-template.md",
    )
    with open(template_path, encoding="utf-8") as f:
        tpl = f.read()

    report = tpl
    for key, val in [
        ("{{NAME}}", data.get("name", "未填写")),
        ("{{DATE}}", data.get("date", date.today().isoformat())),
        ("{{COUNT}}", str(len(questions))),
        ("{{PER_DIM}}", per_dim),
        ("{{CONTEXT}}", data.get("context", "—")),
        ("{{TOTAL}}", f"{total:.1f}"),
        ("{{LEVEL}}", LEVEL_DESC[level]),
        ("{{OVERALL}}", build_overall(total, level, scores)),
        ("{{DIM_TABLE}}", build_dim_table(scores, diagnoses)),
        ("{{LEVEL_BASIS}}", "\n".join(level_basis)),
        ("{{GAPS}}", build_gaps(scores)),
        ("{{DETAIL_TABLE}}", build_detail_table(questions)),
        ("{{PLAN}}", build_plan(scores)),
        ("{{APPENDIX}}", build_appendix()),
    ]:
        report = report.replace(key, val)

    out = args.output
    if not out:
        base = os.path.splitext(os.path.abspath(args.scores))[0]
        out = base + "_报告.md"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 报告已生成: {out}")
    print(f"   综合得分 {total:.1f}/5.0 · 大模型熟悉度 {LEVEL_DESC[level]}")
    for d in DIMENSIONS:
        print(f"   {d}: {scores[d]:.1f} ({tier_of(scores[d])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
