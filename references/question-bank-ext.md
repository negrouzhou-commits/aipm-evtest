# AI PM 测评扩展题库（45 题 · 实战卷）

本卷是 `question-bank.md`（50 题主卷）的**扩展卷**，二者配套使用：主卷覆盖五维 × 三难度的基本盘；本卷偏**进阶 / 挑战**（来自一线公司真实面试题），适合第二轮测评、深度模式或想被"往死里问"的用户。

**来源（全部来自 [landedjobs/ai-interview-questions](https://github.com/landedjobs/ai-interview-questions)，MIT License, Copyright 2026 Landed (b100x)）：**

1. **约 35 题**改编自其 `banks/` 答案库（fde-product-and-gtm.md / llm-and-ml-concepts.md / data-and-applied-science.md / frontier-ai-labs.md）——每题自带成文 "Strong answer"，本卷全文翻译并保留英文原文，双语对照。
2. **10 题**来自其 `roles/ai-product-manager.md` 的 **Reported 真题**（候选人报告或公开来源证实、确实被问过，标注了提问公司：OpenAI / Anthropic / Google DeepMind / Microsoft / Scale AI / Mastercard）。landed.jobs 答案页对 Reported 题只提供 4 步答题结构提示，不含成文答案——这 10 题的中文完整答案由本卷按该结构编译，已如实标注。

**本卷的加工（原素材没有的）：**

- **五维映射**：原素材按 FDE / ML / Data Science 等职能分组，此处重映射到五维能力模型
- **及格要点 / 优秀要点二分**：原素材每题只有一段 Strong answer，此处拆成两层以支持 1-5 分评分
- **变体标注**：与主卷同主题的题标了「变体：XXn」，跨轮次选题时避免同主题连续出现
- **难度映射**：源题的 Easy→基础、Mid/Medium→进阶、Mid-senior/Senior/Hard→挑战

**难度分布提示**：本卷整体偏难（挑战 26 题 / 进阶 15 题 / 基础 4 题）。被测评者第一次测评用主卷；扩展卷用于二测或用户主动要求"更难/更贴近真实面试"时。E 维与 S 维在本卷无基础题，属正常（一线公司这两块本来就不出送分题）。

第三方许可声明见仓库根目录 `THIRD-PARTY-NOTICES.md`。

---

## A. 技术认知（T · 5 题）

### XT01 · 进阶 ｜ 变体：T02
**题干：** RAG 和微调到底差在哪？什么情况下选 RAG，什么情况下选微调？给出你的决策判据。
**及格要点：** 能说清机制差异——微调改权重、固化行为与风格但不新增可靠知识；RAG 接外部检索、知识可随时更新且能给出引用；知道知识常变走 RAG、要稳定语气格式走微调、两者可叠加。
**优秀要点：** 给出成体系的决策树（知识是否演进？瓶颈是风格还是事实？算力预算能否摊薄到百万级调用？）；提到组合拳（微调管语气与安全、RAG 管事实）；能结合成本对比（RAG 改索引即可、微调要训练基础设施与人力周）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #32，MIT）：**

> Fine-tuning adjusts the weights of an existing LLM on a task-specific dataset to bake in behavior — expensive (training infra, MLE weeks), better at adapting style, format and behavior, but doesn't add new knowledge reliably. RAG attaches an external retriever (BM25, dense embeddings) and injects passages into the prompt — cheap to update (just swap the corpus), gives attribution, but is bounded by context window, retrieval quality, and budget. Default to RAG when the data is large, evolving, or needs attribution; fine-tune when the task requires consistent voice/format and the dataset is small and frozen. Combine both: fine-tune the base for tone and safety; RAG for facts. Decision tree: (1) is knowledge evolving? RAG. (2) is voice/style the bottleneck? FT. (3) compute budget? RAG cheaper; FT when you can amortize across millions of queries.

**中文参考答案：**

> 微调是在任务数据集上调整现有模型的权重、把行为"焊"进模型——贵（训练基础设施 + 工程师数周），擅长固化风格、格式和行为，但不能可靠地新增知识。RAG 是外挂检索器（BM25 / 向量召回），把命中的片段注入提示词——更新极便宜（换语料即可）、能给出处，但受限于上下文窗口、检索质量和预算。默认规则：数据量大、常变、需要引用溯源 → RAG；任务要求一致的语气/格式、数据集小且稳定 → 微调。两者可组合：微调打底管语气与安全，RAG 管事实。决策树：① 知识是否在演进？是 → RAG；② 瓶颈是风格不是事实？是 → 微调；③ 算力预算？RAG 便宜，微调只有在能摊薄到百万级查询时才划算。

</details>
**追问：** 什么时候值得微调 embedding 模型？RAG 的质量怎么评？

### XT02 · 进阶 ｜ 变体：T04
**题干：** 要做一个面向客户的"搜索即答"系统，你会在 Prompt、微调、RAG 三者里怎么选、怎么搭？把成本账也算了。
**及格要点：** 选 Prompt + RAG 而不是微调（语料大、在演进、需要引用）；能画出基本链路：向量召回 top-50 → 重排 → top-5 进提示词并带引用。
**优秀要点：** 有完整的成本与架构账——小模型（约 400M）做 embedding 与重排、7-70B 的 LLM 生成答案且前面挂缓存；高频查询改写后缓存结果；成本按 tokens/次 × 单价 × MAU 估；低置信度时默认短回答作为护栏；知道只有当用户评测暴露一致的风格/格式问题时才考虑微调。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #34，MIT）：**

> Architect the funnel: cheap embedding retrieval (top-50) → rerank with cross-encoder → top-5 chunks → prompt with citations. Use a small open model for embedding/cross-encoder (~400M params) and a 7-70B LLM for answer generation behind a cache. Cache retrieved chunks by query rewrite; cache answers for high-frequency queries. Choose prompt + RAG over fine-tune because the corpus is large, evolving, and attribution is needed. Only fine-tune if user eval turns up consistent voice/format issues. Track cost: tokens/call × $/token × MAU; expose a guardrail that defaults to short answers for low confidence.

**中文参考答案：**

> 架构漏斗：便宜的向量召回（top-50）→ 交叉编码器重排 → top-5 片段 → 带引用进提示词生成答案。embedding 和重排用约 400M 的小开源模型，答案生成用 7-70B 的 LLM，前置缓存。检索结果按查询改写缓存、高频查询缓存现成答案。选 Prompt + RAG 而非微调，因为语料大、在演进、必须可溯源。只有当用户评测持续暴露风格/格式问题时才微调。成本按每次调用的 token 数 × 单价 × 月活估算；低置信度场景护栏式地默认给短回答，避免长输出的成本失控。

</details>
**追问：** 什么情况下你会对某个查询切片换成微调过的小模型？

### XT03 · 挑战
**题干：** LLM 系统的线上可观测性和传统 ML 系统的可观测性有什么本质区别？你会监控哪些东西？
**及格要点：** 指出开放输出（没有固定标签 schema）、非确定性（采样温度）、提示词频繁悄悄变更、失败形态模糊（幻觉/拒答过度都算失败但不是二分类）；会记全轨迹日志并采样做评测。
**优秀要点：** 完整列出监控四件套——全轨迹日志（提示词/检索上下文/模型版本/原始输出/工具调用/成本/延迟/用户反馈）、对线上采样数据跑评测管线、输入+输出双向漂移检测（embedding 主题偏移）、变更前在冻结任务集上回归测试；点出"按任务成本而不是按调用成本报警"、评测指标劣化与流量结构变化都要告警。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #40，MIT）：**

> LLM observability requires: (1) full trajectory logs: prompt, retrieved context, model version, raw output, tool calls, cost, latency, user feedback; (2) eval pipelines running on sampled production data; (3) drift detection: both input drift (embedding-based topic shifts) and output drift (semantic embedding of responses, LLM-judge scores over time); (4) regression testing on a frozen task bank before every model or prompt change; (5) user feedback collection (thumbs, edits, follow-ups). Unlike classical ML observability: (a) outputs are open-ended (no fixed label schema); (b) the system is non-deterministic: sampling temperature matters; (c) prompts change frequently and silently drift; (d) "failures" are nuanced (hallucinations, factual errors, refusing too much) and not binary. Senior view: track cost-per-task not per-call, alert on both eval metric degradation and traffic shifts.

**中文参考答案：**

> LLM 可观测性需要：(1) 全轨迹日志：提示词、检索上下文、模型版本、原始输出、工具调用、成本、延迟、用户反馈；(2) 对线上采样数据跑评测管线；(3) 漂移检测：输入漂移（基于 embedding 的主题偏移）+ 输出漂移（回答的语义 embedding、LLM-judge 分数随时间变化）；(4) 每次模型或提示词变更前，在冻结任务集上做回归测试；(5) 收集用户反馈（点赞点踩、编辑、追问）。与传统 ML 可观测性的区别：(a) 输出是开放式的，没有固定标签 schema；(b) 系统非确定性，采样温度都有影响；(c) 提示词频繁变更且会悄悄漂移；(d) "失败"是模糊的（幻觉、事实错误、过度拒答），不是二分类。资深视角：按"每任务成本"而非"每次调用成本"跟踪；评测指标劣化和流量结构变化两类都要告警。

</details>
**追问：** 用现成工具（Langfuse / Arize Phoenix / Braintrust）还是自建？

### XT04 · 基础 ｜ Reported 真题 ｜ 变体：T01
**题干：** 给幻觉（hallucination）下一个定义，并说明你会用什么组合拳降低它。
**及格要点：** 定义准确——模型输出了不被事实或给定上下文支持的内容；缓解至少说出检索增强（给它事实来源）、提示词约束（只用上下文作答）、低温度。
**优秀要点：** 缓解组合分层且诚实——RAG 供依据、引用强制可核验、置信度低时拒答/转人工、事后用 claim 级校验；指出幻觉不能归零、只能按"错误代价"管理，并区分事实性幻觉与忠实性幻觉（前者与真实世界不符，后者与给定上下文不符）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：OpenAI / Anthropic / Mastercard 实问。landed.jobs 答案页仅给出 4 步结构提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify what counts as a hallucination in this product's context; ② Compare credible alternatives for reducing them and state the decision criteria; ③ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 定义：模型生成了不被事实依据（或 RAG 场景下的给定上下文）支持的内容，且语气自信、无自发的不确定性提示。降低手段按层组合：① 数据层——RAG 提供可引用的事实来源，检索质量本身要评（召回不准先修检索，不是修模型）；② 提示层——强约束"仅依据上下文作答"+ 强制引用格式；③ 解码层——降温度、约束输出格式；④ 产品层——引用可点开核验、低置信度时明确说"不知道"并转人工、高风险场景（数字、法务、医疗）强制人审。⑤ 度量层——claim 分解后逐条对上下文校验的幻觉率指标，上线后持续监控。关键判断：幻觉无法归零，目标是把"错误代价 × 发生率"压到可接受，并让用户能自救（能核验、能撤销）。

</details>
**追问：** 你的幻觉率指标没有 ground truth 时还有意义吗？

### XT05 · 挑战
**题干：** Hugging Face、Scale、Perplexity 这类 LLM 原生公司面试实际考什么？如果你去面 AI PM 岗，技术深度上要准备到什么程度？
**及格要点：** 能列出核心考点域：tokenization 与词表、预训练 vs 继续预训练、指令微调与 RLHF/DPO、注意力与 KV cache、量化、评测（LLM-judge / 人评 / 基准）、RAG、Agent。
**优秀要点：** 指出这些公司"ML 概念 + LLM + 调试"混在一起考（如 Scale 会考 PyTorch 调参、transformer 调试、数据管线预处理）；PM 备考策略务实——不必会推导注意力公式，但每个概念都要能回答"这对产品决策意味着什么"（如 KV cache → 成本与并发容量；RLHF → 对齐质量与拒答行为的来源）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #38，MIT）：**

> Expect: tokenization & vocab choices; pretraining and continued pretraining trade-offs; instruction tuning and RLHF/DPO; attention math, KV cache, quantization; eval (BLEU/ROUGE, LLM-judges, human eval), scaling laws, MMLU/HELM-style benchmarks, retrieval-augmentation, agents. At Scale AI the coloring involves "ML concepts, LLMs, and debugging" together with PyTorch debugging (hyperparameters, transformer debugging, data pipeline preprocessing).

**中文参考答案：**

> 预期考点：分词与词表选择；预训练与继续预训练的取舍；指令微调与 RLHF/DPO；注意力计算、KV cache、量化；评测（BLEU/ROUGE、LLM-judge、人评）、scaling law、MMLU/HELM 类基准、RAG、Agent。Scale AI 的特色是"ML 概念 + LLM + 调试"一起考，还会考 PyTorch 调参、transformer 调试和数据管线预处理。PM 的准备策略：概念清单要全覆盖，但深度标准是"能翻译成产品含义"——比如被问 KV cache，要能答出它决定推理成本与并发容量；被问 RLHF，要能答出它是拒答行为和对齐质量的主要来源，直接影响产品体验。

</details>
**追问：** 蒸馏、安全过滤、多模态各自会怎么被问到？

---

## B. 产品基本功（P · 12 题）

### XP01 · 进阶
**题干：** 一个 AI 产品体验差，怎么判断该改模型还是改产品？"这是模型问题"和"这是产品问题"你的分界线是什么？
**及格要点：** 有隔离测试意识——先在干净的隔离环境里测模型行为；模型答错了修模型，模型答对了但产品体验仍差，修产品（提示词、脚手架、UI、上下文）。
**优秀要点：** 指出大多数候选人把"产品差"错归因为"模型差"，纪律性 PM 会先剥离再定责；能举出具体例子（模型检索内容正确但 UI 一次性倾倒 10 条结果导致体验差 → 产品问题）；上下文窗口的分配本身也是产品侧可修的杠杆。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #40，MIT）：**

> Test the model's behavior in a clean, isolated harness first. If the model is wrong, fix the model. If the model is right but the product feels wrong, fix the product (prompt, scaffolding, UI, context-window). Most candidates confuse "this product is bad" with "this model is bad." A disciplined PM separates them.

**中文参考答案：**

> 先在干净的隔离环境（harness）里测模型原始行为。模型错了 → 修模型（换模型、微调、改解码）。模型对了但产品体感仍差 → 修产品：提示词、脚手架（工具、流程编排）、UI 呈现、上下文窗口里塞什么和怎么排序。多数候选人把"这产品不行"和"这模型不行"混为一谈；纪律性的 PM 会把两层剥开再定责。典型例子：检索结果本身是对的，但 UI 把 10 条结果一次性倒给用户 → 这是产品设计问题，换再强的模型也没用。

</details>
**追问：** 讲一个你最终选择改产品而不是改模型的例子。

### XP02 · 挑战
**题干：** 把一个新的 AI 功能推向市场（GTM），你的完整计划是什么？上线 30 天后"做得好"长什么样？
**及格要点：** 覆盖用户、价值、成本（算力/工程）、切入点（wedge）、上线指标五个要素；30 天有可量化的成功定义（采纳、留存、延迟、拒答率）。
**优秀要点：** 明确模型约束（rate limit、能力天花板）如何限制 scope 并提前给出应对；给出分阶段 GTM（内测 → 种子客户 → 公开）；算力成本预测有具体方法（按预估用量 × 单价，含免费额度的滥用风险）；把"用户教育"（这个 AI 能干什么、不能干什么）当 GTM 的一等内容而不是附录。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #41，MIT）：**

> Frame the user, the value, the cost (compute / engineering), the GTM wedge, the launch metric. State what "good" looks like in 30 days (adoption, retention, latency, refusal rate). Note the model's constraints (rate limits, capability ceiling) that limit scope.

**中文参考答案：**

> 框架五件套：目标用户是谁、给他们的可感知价值是什么、成本（算力 + 工程投入）、GTM 切入的楔子（先打哪个细分场景）、上线指标。明确写出 30 天后"好"的定义：采纳率、留存、延迟、拒答率各有目标值。同时如实列出模型约束（API 速率上限、能力天花板）如何限制产品范围——哪些场景这版坚决不做。GTM 分阶段：内部狗粮 → 种子客户共创 → 公开发布；每个阶段的门槛指标和回退预案先写好。算力成本按预估调用量 × 单价预测，含免费额度被薅羊毛的风险与限流预案。

</details>
**追问：** 你的算力成本预测怎么做？

### XP03 · 挑战
**题干：** 在一个成熟产品线里上线一个新的 AI 功能（会动存量用户体验），你的发布计划怎么设计才能不伤信任？
**及格要点：** 分批灰度发布；有金丝雀判据（评测集、幻觉率、延迟、投诉率）；有 kill-switch 回退路径。
**优秀要点：** 先影子流量（shadow）再 A/B 再逐级放量；用户沟通是设计的一部分（发布说明、应用内解释卡片——AI 会出错、怎么反馈）；明确模型废弃（deprecation）伤到存量客户时的迁移策略；"金丝雀判据"不是拍脑袋——每项都定阈值和触发动作。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #42，MIT）：**

> Cohort-by-cohort rollout. Define the canary criteria (eval set, hallucination rate, latency, complaint rate). Hold a kill-switch path. Define the user-facing communication strategy (release notes, in-app explainer). Run a one-bucket A/B first where the new feature is shadow behind the flag.

**中文参考答案：**

> 按用户群逐级放量。先定义金丝雀判据：评测集得分、幻觉率、延迟分位、投诉率，每项有阈值和触发动作（继续 / 暂停 / 回退）。全程握着 kill-switch。发布前先让新功能在 feature flag 后跑影子流量（真实流量、用户不可见），再开单桶 A/B，确认无回退后逐 cohort 放量。用户沟通是发布计划的一等公民：发布说明写清"这功能会出错、错在哪类问题、怎么反馈"，应用内首次使用给解释卡片。存量客户依赖旧模型输出的，要有 deprecation 迁移窗口和兼容方案，不能一刀切。

</details>
**追问：** 模型废弃（deprecation）破坏了某个客户的集成，你怎么处理？

### XP04 · 挑战
**题干：** 挑一个 LLM 在生产环境中的常见失败模式，为它设计一套完整的产品响应。
**及格要点：** 失败模式选得具体（不是"会出错"而是"引用是编的"这种）；响应覆盖 UX（提示 + 可核验）和度量（该失败模式的发生率指标）。
**优秀要点：** 三层闭环——UX 层（指示器 + 核验入口）、度量层（如幻觉引用率）、反馈层（用户举报回流成训练/评测数据）；v1 与 v2 分工明确（v1 纯产品侧护栏快速上线，v2 模型侧专项优化）；算出"每修复一单位失败"的成本包线再决定投多少。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #44，MIT）：**

> Pick a specific failure mode (e.g., hallucinated citation). Design a UX response (indicator + verification affordance), a measurement (hallucinated-citation rate), and a feedback loop (escalation to retraining data). State a v1 that is purely product-side (UI guardrail) and a v2 that is model-side (a specialized citation model).

**中文参考答案：**

> 以"编造引用"为例。UX 响应：引用出处可点击核验，核验失败时显式标记"此引用未通过验证"，并给用户替代路径（换一种问法 / 转人工）。度量：幻觉引用率 = 含未通过验证引用的回答占比，按主题切片定位重灾区。反馈闭环：用户举报的坏引用自动进入评测集和再训练候选。版本分工：v1 纯产品侧——UI 护栏 + 强制引用格式 + 低置信度降级，两周能上线；v2 模型侧——专项引用校验模型或微调。决策依据：先测 v1 能把幻觉引用率压掉多少，算"每压降 1% 的成本"，再决定 v2 投不投。

</details>
**追问：** 每修复一单位失败的成本包线是多少？

### XP05 · 进阶
**题干：** 为一个流媒体服务设计一个 AI Agent（不是聊天机器人）。完整走一遍你的设计过程。
**及格要点：** 区分 Agent 与 chatbot（多轮、用工具、有目标导向）；给出 agent 循环（意图识别 → 实体抽取 → 工具调用 → 响应）；定义工具面与拒绝/兜底路径。
**优秀要点：** 从用户 top 3 任务（jobs）出发定义 agent 范围（如"90 秒内帮全家找到都能看的电影"）；工具面具体（搜索、推荐、观看列表、家长控制）；评测体系完整（任务成功率、任务耗时、任务后满意度）；处理"边界 + 尊重用户已拒绝的选择"（已明确拒绝的类型不再推）这类细节。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #45，MIT）：**

> Define the user's top 3 jobs (e.g., "I want to find a movie the whole family will watch in under 90 seconds"). Sketch the agent loop (intent classification → entity extraction → tool calls → response). State the tool surface (search, recommendation, watchlist, parental controls). Define a refusal / fallback path. Define the evals (task success rate, time-to-task, user satisfaction after task).

**中文参考答案：**

> 先定义用户前三大任务，例如"90 秒内找到全家都愿意看的电影""管理孩子的观看权限""找回上周看了一半的剧"。Agent 循环：意图分类 → 实体抽取（成员、时长、题材偏好）→ 工具调用 → 响应。工具面：内容搜索、个性化推荐、观看列表、家长控制。拒绝与兜底：意图不明时反问而不是猜；工具调用失败降级为搜索结果列表。评测三件套：任务成功率、任务耗时（对标 90 秒）、任务完成后满意度。细节：用户明确拒绝过的内容不再出现在推荐里（即使新模型认为匹配）——把"尊重用户已表达的负面偏好"当成 agent 的硬约束。

</details>
**追问：** 模型又推荐了用户明确拒绝过的影片，怎么处理？

### XP06 · 挑战 ｜ Reported 真题
**题干：** 你会怎么改进 Microsoft Copilot？（Microsoft 实问）
**及格要点：** 先定位再动手——说清 Copilot 当前最痛的问题是什么（如指令理解差、在企业文档上效果不稳、响应慢、价值感知弱），至少给两三个改进方向并配可度量目标。
**优秀要点：** 结构化走完整产品改进流程——① 界定问题与用户分层（重度 Office 用户 vs 轻度，企业 vs 个人）；② 按数据找最大痛 点（支持工单、功能使用漏斗、用户调研）；③ 对比可信的改进方案（上下文工程 vs 模型升级 vs 交互重设计）并说清选择标准；④ 落验证：每项改进的评测与线上指标、灰度方案；⑤ 说清"什么证据会让我改主意"。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Microsoft 实问，Hard。landed.jobs 答案页仅给出结构提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify objective, users, constraints, and failure tolerance; ② Diagnose with data (funnel, tickets, research); ③ Compare credible alternatives and state the decision criteria; ④ Finish with validation, rollout, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 第一步先问"改进什么、给谁"：重度企业用户的核心痛点是复杂指令理解与企业文档 grounding 不稳；轻度用户的价值感知弱（不知道能干嘛）。第二步用数据定位：功能使用漏斗（哪些指令高频、哪些失败后放弃）、支持工单分类、用户调研。第三步对比方案：a) 上下文工程（企业知识库接入 + 文档引用）——对 grounding 问题杠杆最大；b) 指令分层交互（把复杂意图拆成向导式）——降低理解失败；c) 场景化入口（会议纪要、邮件起草做成一键）——提升价值感知。按"影响面 × 置信度 ÷ 成本"排序。第四步验证：每项配离线评测（指令成功率）+ 线上指标（周活使用深度、指令完成率、放弃率），灰度放量。收尾说清：如果数据显示 grounding 改进没有带动指令完成率，我会转向交互层方案。

</details>
**追问：** 你的改进如果和 Office 既有功能团队冲突，怎么办？

### XP07 · 进阶 ｜ Reported 真题
**题干：** 你如何排优先级、如何结构化一条 AI 产品路线图？（Google DeepMind 实问）
**及格要点：** 有明确的优先级判据（用户价值 × 置信度 ÷ 成本，或 RICE 变体）；路线图分层（确定性交付 vs 押注模型能力演进）而不是一张扁平 feature 列表。
**优秀要点：** 点出 AI 路线图特有的结构性问题——模型能力每月在变，路线图要按"能力期权的对冲"设计：一部分功能今天的能力就成立，一部分押下代模型；对比两种路线图组织方式（按主题 vs 按时间）并给出选择标准；收尾有验证与监控：每个季度拿什么证据回顾并调整路线图。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Google DeepMind 实问，Medium。landed.jobs 答案页给出 3 步结构：结构化 → 对比方案 → 收尾验证）：**

> Structure hint (from landed.jobs): ① Structure the roadmap around themes and confidence levels; ② Compare alternative roadmaps and state the decision criteria; ③ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 路线图分三层：① 确定层——当下模型能力已验证、纯执行的功能（可靠性/体验打磨类）；② 对冲层——能力临界但可降级交付的功能（模型够不到时自动降级为规则或人工辅助）；③ 期权层——押注 6-12 个月后模型能力跃迁才成立的功能，小投入预研。优先级判据：用户价值 × 实现置信度 ÷ 成本，且"错误的代价"反向加权（高风险场景排后或加人审）。对比两种组织方式：按主题（knowledge work 助手）对长期叙事好，按时间里程碑对利益相关方沟通好——我选按主题组织、内部再拆里程碑。收尾：每季度用"能力层假设是否成立"（新模型评测结果、竞品动态）回顾路线图，明确什么证据触发重排。

</details>
**追问：** 如果模型能力下个季度跳了一档，你的路线图哪些层要重排？

### XP08 · 进阶
**题干：** 线上输出里出现了一个幻觉（编造的引用/数字），现场排查：你会按什么顺序定位和修复？
**及格要点：** 有诊断顺序而不是直接"换更强模型"——先查检索是否找对了片段，再查上下文里有没有、再查提示词约束。
**优秀要点：** 三步诊断纪律化：① 检索 top-k 是否包含正确片段——不包含则修分块/查询改写，跟 LLM 无关；② 片段在上下文里但模型没用——修提示词（"仅依据上下文作答"+ 引用 token）；③ 上下文对、约束对、模型仍编造——降温度、约束解码、加忠实度分类器。顺序是修数据 → 修提示 → 修解码 → 修模型；明确说"别加更多知识"，答案通常是可观测性 + 提示约束。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #36，MIT）：**

> Diagnose in three steps: (1) is the retrieval returning the relevant chunk? Inspect top-k for query; if not, fix chunking or query rewrite, not the LLM. (2) is the chunk in context? If yes, prompt probably not grounded; reinforce "answer ONLY using the context" or use citation tokens. (3) did the model still fabricate? Constrain decoding (e.g., grammar-constrained outputs, lower temperature), or add a faithfulness classifier. Sequence = fix data, fix prompt, fix decoding, fix model. Avoid the trap of "add more knowledge" — usually the answer is observability plus prompt constraint.

**中文参考答案：**

> 三步诊断：① 检索层——看这条 query 的 top-k 片段里有没有正确答案。没有 → 修分块策略或查询改写，别碰 LLM。② 上下文层——正确片段进了上下文但模型没用 → 提示词不够"接地"，加强"仅依据上下文作答"的约束或强制引用 token。③ 模型层——上下文对、约束对、模型仍编造 → 约束解码（语法约束输出、降温度），或外挂一个忠实度分类器拦截。总顺序：修数据 → 修提示 → 修解码 → 修模型，从便宜到贵。警惕"加更多知识"这个直觉陷阱——多数幻觉问题的答案是可观测性 + 提示约束，不是堆语料。上线后持续监控同类失败模式，保持护栏。

</details>
**追问：** 持续监控和护栏具体怎么做？

### XP09 · 基础 ｜ Reported 真题
**题干：** 讲一次你为了更快交付而砍 scope 的经历。砍了什么、留下了什么、结果如何？（Google DeepMind 实问）
**及格要点：** 有真实具体案例（不是"理想情况下我会……"）；说清砍的原则（什么必须留、什么可以后补）和结果。
**优秀要点：** 用因果结构讲：决策背景 → 砍 scope 的原则（按"用户可感知价值"留核心、砍完美度）→ 替代方案对比（为什么不是加人/延期）→ 结果量化 → 学到了什么并泛化；诚实说出代价（砍掉的部分后来补了/被骂了），不粉饰。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Google DeepMind 实问，Easy。landed.jobs 答案页给出 4 步结构）：**

> Structure hint (from landed.jobs): ① Clarify the objective, user, constraints, and acceptable failure modes; ② Structure around decision context, scope principle, outcome, learning; ③ Compare credible alternatives and state the decision criteria; ④ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 用 STAR + 砍削原则的结构：背景（客户上线窗口只有 4 周，全量 scope 要 8 周）→ 砍削原则（按"用户第一条可感知价值路径"倒排：v1 只保留 3 步核心工作流 + 手工兜底，砍掉自动路由、多轮记忆、自助配置）→ 替代方案对比（加人边际产出低且引入协调成本；延期错过客户财年预算窗口；砍 scope 保窗口是三者中风险可控的）→ 结果（v1 两周后上线，客户首月用了核心路径 2000+ 次；砍掉的功能 6 周内按真实使用数据重新排了优先级，其中 40% 被证明根本不需要做）→ 学习：砍 scope 的依据应该是"哪条路径承载用户价值"而不是"哪个功能容易砍"。

</details>
**追问：** 事后看，你砍错了什么？

### XP10 · 基础 ｜ Reported 真题
**题干：** 讲一次你处理冲突优先级的经历。（OpenAI 实问）
**及格要点：** 有真实案例；说清优先级判据是什么（不是"谁声音大听谁"）；干系人对齐的动作和结果。
**优秀要点：** 结构完整：优先级判据（用户影响面 × 紧迫性 × 战略权重）→ 干系人对齐（把判据摆到桌面上对齐，而不是私下各个击破）→ 决定与取舍（谁的需求降级、怎么补偿）→ 结果与复盘；诚实处理"政治"因素——承认上级压力存在，但判据仍然公开透明。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：OpenAI 实问，Easy。landed.jobs 答案页给出 4 步结构）：**

> Structure hint (from landed.jobs): ① Clarify the objective, user, constraints, and acceptable failure modes; ② Structure around prioritization criteria, stakeholder alignment, decision, outcome; ③ Compare credible alternatives and state the decision criteria; ④ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 案例：合规要求的安全评测升级和销售承诺的大客户定制功能撞在同一周，工程资源只有一份。结构：① 先把判据公开化——合规是硬门槛（不做不能上线），定制功能是有合同义务的 P1，两者都"重要"，冲突在资源不在价值。② 对齐动作：拉上合规、销售、工程负责人过同一张表（用户影响面 × 不做的代价 × 可延期性），把"安全评测自动化改造可以拆出一半给数据组"这个资源解法找出来。③ 决定：安全升级保整块，定制功能换人+顺延一周，销售拿着新的时间线去和客户重谈。④ 结果：两条线都按新计划交付；复盘沉淀"资源冲突先找判据共识再找资源解法"，后来成为团队的默认流程。

</details>
**追问：** 如果两个干系人都拒绝让步，你怎么办？

### XP11 · 进阶
**题干：** 讲一次你在完全陌生的领域/环境里（新行业、新客户、新业务）快速产出有效工作的经历。
**及格要点：** 有具体案例；说清学习路径——问谁、读什么、多快产出。
**优秀要点：** 自己设计了学习系统（行业图谱 → 专家访谈清单 → 必读材料），几周内交付了相关成果；有"谦逊但有效"的证据——承认哪里懂了哪里还没懂、避免拿术语唬人；提炼出可迁移的方法论（怎么在新领域快速建立有效认知）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #60，MIT）：**

> Pick an example where you had to absorb a vertical (e.g., supply chain, defense, healthcare) and produce relevant work within weeks. Show how you designed your own learning, who you asked, what you read, and what the output was.

**中文参考答案：**

> 案例：两周内进入一个陌生的供应链行业客户现场。方法：第一周前 3 天画行业地图（上游/中游/角色/钱怎么流，用客户给的 3 份年报 + 2 份券商研报）；随后列出 10 个"只有客户能回答"的问题清单，访谈客户的运营、财务、一线仓管各 1 小时；第二周产出：一张客户现有流程的问题清单（按可 AI 化 × 价值排序）+ 一个最小概念验证。关键姿态：明确说"我理解到 X，还没理解 Y，Y 我需要再跟一线确认"——拿术语唬人在现场会立刻穿帮。可迁移方法论：新领域的快速认知 = 结构化地图（公开材料）+ 定向访谈（问只有内部人能答的问题）+ 尽快做出一个可被纠正的粗稿。

</details>
**追问：** 这段经历里最持久的教训是什么？

### XP12 · 进阶 ｜ Reported 真题
**题干：** 讲一次你和工程师在 Agentic AI 产品上的协作经历——分歧在哪、怎么解决的？（Scale AI 实问）
**及格要点：** 有真实协作案例；说清 PM 与工程师的分工和分歧点（如 agent 自主性边界、工具面设计），以及怎么达成一致。
**优秀要点：** 结构完整：目标与约束 → 分歧的实质（不是权力之争而是风险偏好差异：工程担心 agent 失控不可测、PM 要交付自主性体验）→ 解决机制（用评测数据和失败模式清单代替立场争论——"自主性每加一分，评测集里新增哪类失败必须兜住"）→ 因果链清晰的结果 → 对比过其他协作方式并说明为何选这个。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Scale AI 实问，Medium。landed.jobs 答案页给出 4 步结构）：**

> Structure hint (from landed.jobs): ① Clarify objective, users, constraints, and failure tolerance; ② Cover cross-functional role, technical fluency, trade-offs, outcome in a causal structure; ③ Compare at least two credible approaches; ④ Specify evaluation, rollout, monitoring, and rollback.

**中文参考答案（本卷按该结构编译）：**

> 案例：客服工单 agent，分歧在自主性等级——我要 v1 就能自动执行退款（限额内），工程坚持 v1 只建议不执行。分歧实质是风险偏好：工程担心不可测的级联失败，我担心"只建议不执行"让产品价值感知为零。解决机制：不争立场，改争判据——一起定义"放开自动执行的门槛"：连续 4 周评测集上误判率 < 0.5%、每笔限额 50 元内、全链路可回滚、异常自动熔断。结果：v1 以建议模式上线，3 周数据达到门槛，v1.5 放开限额内自动执行，误判率 0.3%，期间触发熔断 2 次都正确。复盘：PM 和工程的分歧多数可以用"把双方都认的可量化门槛写下来"解决，比谁说服谁都快。

</details>
**追问：** 工程师说你的门槛数据样本不够，你怎么回应？

---

## C. 数据与评估（E · 18 题）

### XE01 · 进阶 ｜ 变体：E10
**题干：** 一个全新 AI 功能的成功指标怎么定义？给出你的指标体系分层。
**及格要点：** 有分层意识——北极星 + 支撑指标 + 护栏；能说出至少一个离线指标、一个在线指标。
**优秀要点：** 层级模型完整：北极星（任务完成率）+ 支撑（正确性、延迟、幻觉率、单位任务成本）+ 护栏（转人工率、有害输出率）+ 行为指标（长期留存）；每层说清为什么放那层；离线/在线不一致时的仲裁规则（线上管真相）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #38，MIT）：**

> Use a layer-cake model: top-line North Star (e.g., task completion), supporting metrics (correctness, latency, hallucination rate, cost-per-task), and guardrails (escalation rate, harmful-output rate). State one offline metric (eval set), one online metric (live task success), and one behavioral metric (long-term retention).

**中文参考答案：**

> 用分层蛋糕模型：顶层北极星指标——任务完成率（用户带着任务来、任务被解决了才算数）；中间支撑指标——正确性、延迟分位、幻觉率、单位任务成本；底层护栏指标——转人工率、有害输出率、投诉率，任何一项恶化都否决"整体变好"的结论。三类各举一例：离线指标（评测集上的任务成功率）、在线指标（线上真实任务完成率，用后续行为或抽检标注）、行为指标（长期留存——短期新鲜感退潮后还在用）。仲裁规则：离线和线上不一致时，线上管真相，离线用来定位原因。

</details>
**追问：** 离线指标和线上指标打架了，你怎么办？

### XE02 · 挑战 ｜ 变体：E01
**题干：** 给一个要交付企业客户的 LLM 新功能设计完整的评测策略。
**及格要点：** 覆盖离线回归 + 线上灰度两个阶段；有人工评测的位置；有对抗样本意识。
**优秀要点：** 体系完整——从 200 条人工标注起步、用线上失败持续扩集；回归集上用 bootstrap 算置信区间；LLM-as-judge 上量但锚定在已知分布子集上防漂移；红队集专收对抗 case；发布走 feature flag + 5% 影子流量再放量；能回答"评测集什么时候过期"（线上分布漂移检测触发重建）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #39，MIT）：**

> Start with 200 hand-labeled examples; grow the set from production failures. Define a confidence interval method for the regression set (bootstrapping). Add an LLM-as-judge for higher volume but cap it on a known-distribution subset. Define a red-team set for adversarial cases. Ship behind a flag and shadow 5% of traffic before ramp.

**中文参考答案：**

> 起步：200 条人工标注样本覆盖典型场景 + 已知失败模式；此后评测集不是静态的——线上失败 case 每周回流进集，形成生长机制。回归集上的指标用 bootstrap 算置信区间，避免"涨了 2 分"实际是噪声。上量：LLM-as-judge 处理大批量，但必须锚定——固定一个已知分布的子集，定期用人工标注校验 judge 本身没有漂移。对抗：单独维护红队集（提示注入、诱导违规、边界输入）。发布：feature flag 后先跑 5% 影子流量（真实流量、不外露），指标全部达标才逐级放量。评测集过期判定：线上输入分布漂移检测（embedding 主题偏移）显著时触发集重建。

</details>
**追问：** 你怎么发现评测集已经过期了？

### XE03 · 挑战
**题干：** "你会怎么度量 X？"——以一个企业级功能为例，走一遍你构建度量方案的完整过程。（Anthropic 分析轮实题型）
**及格要点：** 先定义用户结果再选指标（不是上来列指标）；有先行指标 + 滞后指标的拆分。
**优秀要点：** 五步完整：① 定义用户结果；② 拆先行指标（与结果相关的使用行为）与滞后指标（结果本身）；③ 设计实验（RCT / 前后对比 / 准实验，说明各自适用与代价）；④ 定回退判据；⑤ 并行跑一个公平性/安全指标；能回答样本量估算（功效分析的基本逻辑）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #43，MIT）：**

> Step 1: define the user outcome. Step 2: decompose into a leading indicator (usage that correlates with outcome) and a lagging indicator (the outcome itself). Step 3: design the experiment (RCT, pre/post, or quasi-experimental if RCT is infeasible). Step 4: define the rollback criterion. Step 5: include a fairness / safety metric that runs in parallel.

**中文参考答案：**

> 五步法：① 先写"用户结果"一句话定义——如企业知识库问答功能，结果是"员工用自助问答替代了找 IT/同事人工答疑"。② 拆先行/滞后：先行指标（周活跃提问数、答案采纳率、追问率——行为层，周内可见）；滞后指标（IT 工单量下降比例、员工满意度——结果层，季度可见）。③ 实验设计：能随机分组就 RCT（按部门/团队随机）；不能随机（企业客户往往不能）用前后对比 + 对照组，或断点回归等准实验，并说明各自的可信度损失。④ 回退判据先行：答案采纳率连续 2 周低于基线 X% 即回退。⑤ 公平性/安全指标并行：幻觉率、敏感数据泄露检测，不进 A/B 但持续监控。样本量：按预期效应量做功效分析，效应越小所需样本越大。

</details>
**追问：** 样本量怎么算？

### XE04 · 挑战
**题干：** 新模型版本上线后，北极星指标掉了 1%。讲讲你接下来 10 天每天在干什么。
**及格要点：** 先验证回退是真实的（统计功效、分用户群切片）而不是噪声；决定放量暂停/回退/前修。
**优秀要点：** 三问框架：真实吗（统计功效、分位分析）→ 集中吗（哪个 cohort、哪类 prompt）→ 持续吗（3 天趋势）；对应动作：暂停在当前 ramp、下钻离线评测 vs 线上 delta、回退/前修/继续的判据；明确"谁拍板"和客户沟通计划；10 天的节奏有日粒度（前 3 天诊断、中 4 天下钻与决策、后 3 天执行与复盘）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #47，MIT）：**

> Triangulate: is the regression real? (statistical power, segmentation). Is it concentrated? (which user cohort / which prompt type). Is it persistent? (trend over 3 days). Then triage: hold the rollout at the current ramp, dig into the eval set vs. online delta, decide whether to roll back, fix-forward, or continue. State the comms plan to the customer.

**中文参考答案：**

> 三角验证三问：① 真的吗——1% 在当前流量下统计功效够吗？做分用户群切片，看是整体滑落还是某 segment 拖累。② 集中吗——哪类 prompt、哪类任务、哪个 cohort 掉得最狠；离线评测集上有没有复现（复现 → 已知回归；不复现 → 分布或交互问题）。③ 持续吗——看 3 天趋势，单日抖动不动手。据此分诊：先冻结在当前放量位不动（不自动全量也不回退）；下钻离线 vs 线上的 delta 定位根因；回退 / 前修 / 继续的判据提前写死（如集中且持续 → 回退；分散且 <1% → 前修加护栏继续）。拍板人明确（值班 PM + 工程负责人双人确认），客户沟通（如企业客户）在回退决定当天发出。10 天节奏：D1-3 验证与定位，D4-7 决策与方案，D8-10 执行、复盘、评测集补案例。

</details>
**追问：** 谁来拍板？

### XE05 · 挑战
**题干：** LLM-as-judge：它有哪几种用法、怎么校准、会在哪里翻车？什么时候必须换人？
**及格要点：** 说清三种模式（单点打分 / 成对比较 / 对照标准答案）；知道要拿更强的模型当裁判、要人工抽检校准；能列至少两个失效模式（位置偏差、长度偏差）。
**优秀要点：** 失效清单完整——位置偏差（A/B 顺序影响判断，双向跑取平均）、长度偏差（长回答被高估）、自我偏好（裁判偏爱自己的风格）、格式偏差、领域盲区（人能看出来专家级错误，LLM 裁判看不出来）；量级判断：LLM-as-judge 对 70-85% 的 case 可靠，高风险结论必须人抽检；成对胜率是在线 A/B 最稳的指标。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #39，MIT）：**

> LLM-as-judge uses a (usually stronger) LLM to score, classify, or compare outputs of another LLM. Three modes: (1) pointwise: judge a single answer on a rubric; (2) pairwise: judge "A vs B" which is better; (3) reference-based: judge against a gold answer. Practical recipes: structured rubrics (CoT scoring prompts, criteria-based chains), use a stronger model than the candidate, calibrate against a human-labeled set. Failure modes: (1) position bias: "A vs B" output depends on order; mitigate by averaging both orderings; (2) length bias: longer answers judged better; (3) self-preference: judge favors its own style; (4) format bias; (5) rubric-blind evaluation: LLM judges miss domain-specific errors a human expert catches. Senior view: LLM-as-judge is reliable for ~70-85% of cases but ALWAYS needs human spot-audits for high-stakes claims. Pairwise comparison with win-rate is the most stable metric for online A/B testing.

**中文参考答案：**

> 定义：用一个（通常更强的）LLM 给另一个 LLM 的输出打分、分类或比较。三种模式：单点式（按 rubric 给单个答案打分）、成对式（判断 A vs B 谁更好）、参考式（对照金标准答案判）。实操配方：结构化 rubric（CoT 评分提示、按维度链式打分）、裁判模型强于被评模型、定期用人工标注集校准裁判本身。失效模式五连：① 位置偏差——A/B 顺序影响结论，双向各跑一次取平均来对冲；② 长度偏差——更长的回答被系统性高估；③ 自我偏好——裁判偏爱与自己相似的风格；④ 格式偏差——markdown 结构好看的得分虚高；⑤ rubric 盲区——人能看出的领域专家级错误，裁判看不出来。资深判断：LLM-as-judge 对约 70-85% 的 case 可靠，但高风险结论永远需要人工抽检兜底；在线 A/B 里最稳定的指标是成对比较胜率。

</details>
**追问：** 怎么纠正这些偏差？什么场景必须人评？

### XE06 · 挑战
**题干：** 模型/提示词每次变更发布前，你的回归测试体系长什么样？多大才够？
**及格要点：** 有冻结评测集的概念；变更前全量跑 + 阈值门禁；知道"5 条手写查询"这种规模是在自欺。
**优秀要点：** 体系完整——200-2000 条代表性任务 + 金标准标签；跑三类检查（自动化指标：忠实度/相关性/任务成功率；LLM-as-judge 与上一版成对比较；成本与延迟回归）；50 条高风险金丝雀集重点盯；CI 里存历史、按指标设 pass/fail；量级观点：滚动维护约 5000 条混合金标 + A/B 轨迹的集，多样性比数量更重要（过拟合成个别措辞的集比没有还糟）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #41，MIT）：**

> Build a frozen eval set of 200-2000 representative tasks with ground-truth labels (human or LLM-curated). Before each model/prompt/RAG corpus change ships, run all tasks through the candidate system, compute (1) automated metrics (RAGAS-style faithfulness, answer-relevance, task success rate); (2) LLM-as-judge pairwise comparison against the previous version; (3) cost/latency regression checks. Maintain a canary set: ~50 high-stakes queries you monitor even harder. Store results in CI with pass/fail thresholds per metric. Senior nuance: regression test suites must be diverse enough to catch subtle regressions: "5 hand-written queries" is worse than useless (overfits to individual prompt phrasings). Real practice: maintain a rolling 5000-query set that mixes gold labels with paired A/B trajectories.

**中文参考答案：**

> 建一个冻结评测集：200-2000 条带金标准标签（人工标注或 LLM 精筛后人工复核）的代表性任务。每次模型/提示词/语料变更发布前，把全部任务跑过候选系统，算三类结果：① 自动化指标（RAGAS 式忠实度、答案相关性、任务成功率）；② LLM-as-judge 与上一版本的成对比较；③ 成本与延迟回归检查。另维护约 50 条高风险金丝雀查询，盯得比大盘更紧。结果进 CI 留存，每个指标有 pass/fail 阈值。规模判断：评测集的多样性比数量重要——"5 条手写查询"比没有还糟（过拟合个别措辞，给出虚假信心）。真实实践：滚动维护约 5000 条的集，混合金标答案和成对 A/B 轨迹，持续吐故纳新。

</details>
**追问：** 评测集多大才够？什么指标阈值触发回退？

### XE07 · 挑战
**题干：** 评估 LLM 该用哪些 benchmark？MMLU、GSM8K、HELM 各自测什么、各有什么坑？
**及格要点：** 知道三者的定位差异——MMLU 测知识广度、GSM8K 测推理、HELM 测多轴综合；知道数据污染（contamination）这个词。
**优秀要点：** 能批判而不只是列举——MMLU 的多选题格式假设 + 污染嫌疑；GSM8K 配 CoT 评测、与 MMLU 互补（考连贯推理而非知识记忆）；HELM 是"多维测量"的正确引用（准确、校准、鲁棒、偏见、公平、效率）；2026 视角：SWE-Bench、tau-bench、FrontierMath、GPQA Diamond、Chatbot Arena Elo 已取代 MMLU 成为主信号；抗污染新基准靠 held-out 题目、动态生成、人抽检。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #42，MIT）：**

> MMLU: 57 multi-domain academic knowledge tests, multi-choice, measures capability breadth, but criticized for contamination, narrow formatting bias, and the "all you need is one correct answer" assumption. GSM8K: grade-school math word problems, classic reasoning benchmark, paired with chain-of-thought evaluation; complementary to MMLU because it tests coherence over knowledge. HELM (Stanford, Liang et al. 2022): holistic evaluation across many axes (accuracy, calibration, robustness, bias, fairness, efficiency), the correct citation when an interviewer wants you to argue for multi-axis measurement. Senior view: as of 2026, harder reasoning benchmarks (SWE-Bench, tau-bench, FrontierMath, GPQA Diamond) and human-preference-based ones (Chatbot Arena Elo) have eclipsed MMLU as the "real" signal. Newer "contamination-resistant" benchmarks use held-out questions, dynamical generation, or human spot-audits.

**中文参考答案：**

> MMLU：57 个领域的选择题知识考试，测能力广度；坑：训练数据污染嫌疑、格式窄（选择题假设"只有一个正确答案"）。GSM8K：小学数学应用题，经典推理基准，配合思维链评测；与 MMLU 互补——考的是推理连贯性而不是知识记忆。HELM（斯坦福，Liang 等 2022）：多轴综合评测（准确率、校准、鲁棒性、偏见、公平、效率），当面试官想听"多维度测量"的论证时引用它最正确。资深视角：到 2026 年，更难的推理基准（SWE-Bench、tau-bench、FrontierMath、GPQA Diamond）和基于人类偏好的（Chatbot Arena Elo）已经取代 MMLU 成为"真信号"。新一代抗污染基准用 held-out 题目、动态生成、人工抽检来防泄漏。落到 PM 实践：选型时不要拿单个基准分当决策依据，按你的任务类型选对应基准，再加自建业务评测集。

</details>
**追问：** 什么是基准污染？你怎么追踪模型在真实世界的质量？

### XE08 · 挑战
**题干：** 线上 LLM 应用的输入分布漂移（distribution shift）怎么监测？
**及格要点：** 有输入漂移的概念（用户问的问题类型在变）；知道 embedding 聚类/主题偏移这个手段。
**优秀要点：** 三层监测：① embedding 主题漂移——采样入库、聚类、滚动窗口对比（1 天 vs 7 天）top-K 簇心距离告警；② 词法层——token 分布、语言混比、平均长度、特殊字符比例（提示注入标记）；③ 裁判分漂移——抽 1% 输出跑 LLM-as-judge，分数下滑或方差膨胀告警；资深 nuance：输入漂移常比质量劣化早几天出现，是早期预警；计划内变更（新 UI 字段）会误报，要能区分；对抗性漂移（有人故意改写攻击）单独识别。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #43，MIT）：**

> Three layers: (1) embedding-based topic shift: sample incoming queries, embed, cluster, compare cluster distribution over rolling window (e.g., 1 day vs. 7 days); alert when top-K cluster centroids move > X distance. (2) lexical shift: watch token distribution, language mix, average length, special-character ratio for prompt injection markers. (3) judge metric drift: sample 1% of outputs, run LLM-as-judge, alert when judge scores fall > Y or variance grows. Tools: Arize Phoenix, whylogs, Evidently, custom Prometheus dashboards. Senior nuance: input drift often precedes model-quality degradation by days: early warning reduces incidents. Beware of false positives during scheduled feature changes (e.g., new UI fields).

**中文参考答案：**

> 三层监测：① embedding 主题漂移——采样线上 query，向量化、聚类，滚动窗口对比分布（如近 1 天 vs 近 7 天），top-K 簇心移动超过阈值就告警。② 词法漂移——盯 token 分布、语言混比、平均长度、特殊字符比例（后两者同时是提示注入的标记）。③ 裁判分漂移——抽 1% 输出跑 LLM-as-judge，均分下滑或方差膨胀就告警。工具：Arize Phoenix、whylogs、Evidently 或自建 Prometheus 面板。资深 nuance：输入漂移往往比模型质量劣化早几天出现，是免费的早期预警系统，能显著减少事故。但要防误报：计划内功能变更（新 UI 输入字段）天然引发漂移，告警规则要把这类"已知变更"挂白名单。

</details>
**追问：** 漂移不一定意味着真变化——什么时候不报警？什么是对抗性漂移？

### XE09 · 挑战 ｜ 变体：E05
**题干：** 不靠昂贵的人工评测，怎么测量和持续监控幻觉率？
**及格要点：** 知道 LLM-as-judge + claim 分解的路线（把答案拆成原子断言逐条对上下文校验）；知道没有 ground truth 的幻觉率没有意义。
**优秀要点：** 从便宜到贵的完整菜单——① judge + claim 分解（与人工一致性较高但裁判有偏差）；② 自一致性（N 次采样看语义分歧度，对事实性问题不可靠）；③ 有金标准时逐条对照；④ 人工抽检 1-5% 做金标准；工具点名（DeepEval HallucinationMetric、Vectara HHEM 榜单）；指出必须配一个带标签的校验集来校准这个指标本身。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #44，MIT）：**

> Hallucination rate is the fraction of outputs that contain content not supported by ground truth (or context, in RAG). Measurement options from cheap to expensive: (1) LLM-as-judge with claim decomposition: split answer into atomic claims, judge each against context; high agreement with humans but judge-bias. (2) Self-consistency: sample N answers, measure inter-sample semantic disagreement; unreliable for factual claims. (3) Reference-based: if you have a gold answer, judge each claim against the gold. (4) Human eval: gold standard, expensive, sampled 1-5%. Tooling: DeepEval's HallucinationMetric, Patronus Lynx, Vectara HHEM leaderboard. Senior view: hallucination rate without a defined ground truth is meaningless: always pair with a labeled validation set to calibrate the metric.

**中文参考答案：**

> 定义：幻觉率 = 含"不被 ground truth（RAG 场景下即给定上下文）支持的内容"的输出占比。测量菜单按成本排序：① LLM-as-judge + claim 分解——把答案拆成原子断言、逐条对照上下文判支持/不支持，与人工一致性较高，但裁判自身有偏差；② 自一致性——同一问题采样 N 次看语义分歧度，便宜但对事实性断言不可靠；③ 参考式——有金标准答案时逐条对照金标；④ 人工评测——金标准，贵，抽 1-5% 做锚。工具：DeepEval 的 HallucinationMetric、Patronus Lynx、Vectara HHEM 榜单可横向参考。资深观点：没有明确 ground truth 的幻觉率是无意义的数字——必须配一个带标签的校验集定期校准指标本身，否则指标会随裁判漂移悄悄失真。

</details>
**追问：** 你的评测集要多大，才能相信"提升 1%"是真的？

### XE10 · 挑战
**题干：** 线上怎么 A/B 测试两个提示词或两个模型？和传统 A/B 有什么不同？
**及格要点：** 知道成对比较/胜率比绝对打分稳；有护栏指标（延迟 p99、幻觉率、拒答率、成本）；知道"预定样本量、不要中途偷看"。
**优秀要点：** 2025-2026 最佳实践：交错式（interleaved）测试抵消时段效应；主观质量没有二元标签时用 LLM-judge 成对胜率 + 置信区间；功效分析量级感——51% vs 49% 的小差异要几万次比较才能显著；资深警告：绝不一次性全量切换（无法分离"模型变化"和"用户适应"）；长尾/重度用户单独切片分析。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #45，MIT）：**

> Best practice 2025-2026: (1) interleaved A/B testing: randomly assign user requests to candidate A or B but interleave to control for time-of-day effects; (2) primary metric: task success rate (binary label, LLM-judge calibrated against humans) or user thumbs/retention if available; (3) guardrail metrics: latency p99, hallucination rate, refusal rate, cost-per-task. Stop after pre-set sample size (don't peek). For subjective quality without binary labels: pairwise comparison via LLM judge; measure win-rate with statistical confidence intervals. Senior view: power analysis for win-rate is tricky: small absolute differences (e.g., 51% vs 49%) require tens of thousands of comparisons to call. Always run interleaved, never switch all-at-once: you cannot disentangle "model change" from "user adaptation".

**中文参考答案：**

> 2025-2026 最佳实践：① 交错式 A/B——用户请求随机分给候选 A/B，但交错分布以抵消时段效应（早晚流量质量不同）；② 主指标：任务成功率（二元标签，LLM-judge 需先对人工校准）或用户点赞/留存；③ 护栏指标并行：延迟 p99、幻觉率、拒答率、单位任务成本，任一恶化即停。样本量预定，中途不偷看结果（peeking 会虚增假阳性）。主观质量无二元标签时：LLM-judge 成对比较，报胜率 + 置信区间。资深量级感：胜率的功效分析很讲究——51% vs 49% 这种小差异要几万次比较才能下结论，别拿两千次就宣布获胜。铁律：永远交错实验，绝不一次性全量切换——全量切换后你无法把"模型变好"和"用户适应了"分开。

</details>
**追问：** 长尾重度用户切片怎么处理？

### XE11 · 进阶
**题干：** 面试官追问："你为什么给这个产品选 RAG 而不是微调？你的幻觉到底是怎么评的？"——给出能顶住追问的答案。
**及格要点：** 选型理由具体（微调在该数据规模下成本不划算）；幻觉评测有具体指标（judge + 人工抽检）而不是"我们测过，还行"。
**优秀要点：** 全链路可辩护——选型：微调成本在该数据量级不成立，MiniLM 检索速度 + 语义分块策略把幻觉率降了 40%；评测：LLM-judge 对照 held-out 金标集 + 分层人工抽检，另加检索精度（被引用片段实际进入最终答案的比例）和事实准确通过率；按主题切片暴露检索弱区；能答"边界 case 的 groundedness 怎么判"和"什么证据会让我转向微调"。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #33，MIT）：**

> Explain that fine-tuning was cost-prohibitive on the dataset, so we used MiniLM for retrieval speed and a semantic-chunking strategy that dropped hallucination rate by 40%. Present the eval: an LLM-judge against a held-out gold set, paired with human spot-check on a stratified subset, plus retrieval-precision (fraction of retrieved chunks used in the final answer) and factual-accuracy pass rate. Slice by topic to surface where retrieval fails.

**中文参考答案：**

> 选型辩护：微调在该数据集规模下成本不成立（训练基础设施 + 数周人力 vs RAG 换索引当天生效），所以走 RAG：MiniLM 做检索（速度优先），语义分块策略（按语义边界而非固定长度切）把幻觉率压降 40%。评测体系：LLM-judge 对照 held-out 金标集打分 + 分层人工抽检校准；检索精度（召回片段实际被答案引用的比例）单独追踪，因为它把"检索失败"和"生成失败"分开了；再加事实准确通过率。按主题切片：暴露哪类主题检索最弱（通常是术语歧义多的），优先补同义词表和查询改写。边界 case 的 groundedness 判定走仲裁队列，两人背靠背，分歧样本进金标集。转向微调的触发条件：如果风格/格式类差评持续占大头且 RAG 侧无解。

</details>
**追问：** 边界 case 的 groundedness 怎么判？什么时候你会转向微调？

### XE12 · 进阶
**题干：** 一个效率类 App 的"用户参与度"怎么度量？要跟踪哪些功能和行为？
**及格要点：** 北极星 + 次级指标配对；参与度不能以牺牲信任为代价（有反指标意识）。
**优秀要点：** 北极星定义精准（周活跃创作者 + 至少一件实质性产出，不是"打开 App"）；次级（任务完成不放弃率）+ 功能级（编辑率、分享频率）；反指标护栏（工单量、隐私退出数）防止用暗黑模式刷参与度；按参与/留存/满意度分面板切片；埋点在采集时定义清楚，避免事后无法回溯。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #55，MIT）：**

> Pair a north-star with hygiene metrics. North-star: weekly active creators with one substantive artifact. Secondary: time-on-task completed without abandonment; feature-specific: list-edit rate, share frequency. Anti-metric: support tickets and privacy opt-outs — so engagement doesn't grow at the cost of trust. Decouple via dashboard slice: engagement vs retention vs satisfaction scores. Define features and behaviors to log at ingestion time so the metric isn't deadlock-locked.

**中文参考答案：**

> 北极星配卫生指标。北极星：周活跃"创作者"数（以产出至少一件实质作品计）——不是"打开 App"，是完成闭环。次级指标：任务完成不放弃率、单任务净耗时；功能级：列表编辑率、分享频率。反指标护栏：支持工单量、隐私设置退出数——参与度涨但这两个也在涨，说明在用暗黑模式（无意义推送、诱导点击）透支信任。看板分三个切片（参与度 / 留存 / 满意度）解耦观察，避免单一面板误导。工程前置：埋点字段在采集时就定义好（哪些行为算"参与"事件、带什么维度），否则指标口径事后改不了，等于锁死。

</details>
**追问：** 怎么防古德哈特定律（指标被优化成目标后就失真）？

### XE13 · 进阶
**题干：** 100 万用户在注册后第 6 个月左右集中流失。你的调查框架是什么？
**及格要点：** 把问题转成可证伪的假设列表（人群漂移 / 新鲜感衰减 / 6 个月硬摩擦 / 外部竞争），而不是直接拍结论。
**优秀要点：** 假设四分法+ 验证工具配齐——同期群（cohort）拆解看新 cohort 是否不同；月度订阅弹性曲线找 6 个月点的硬摩擦（续费、算法变噪音）；功能使用热力图看衰减先发生在哪；反事实干预：给 5% 切片发第 6 个月定向挽留触达，测 30 天留存差；先跑最便宜的实验再上重方案。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #56，MIT）：**

> Hypothesis space: (1) user-mix drift (new cohorts are different), (2) experiential decay (the novelty fades), (3) hard friction at the 6-month mark (e.g. renewal/billing/algorithm getting noisier), (4) external (competitor ads). Triangulate via cohort breakdown, monthly subscription-elasticity curve, feature-use heatmap, and a counterfactual holdout where you intervene with a 6-month nudge. Pick a low-cost experiment: send a re-engagement nudge to a 5% slice; measure 30-day retention delta.

**中文参考答案：**

> 假设空间四类：① 人群漂移——新注册 cohort 画像变了（渠道投放变化拉来不同的人），拆同期群对比验证；② 体验衰减——新鲜感自然消退，看功能使用热力图确认衰减从哪些功能先开始、是否逐月平滑下降；③ 6 个月硬摩擦——续费/扣款失败、推荐算法在积累噪音，查月度订阅弹性曲线在 6 个月点有没有台阶；④ 外部因素——竞品在同一时段的投放。三角验证：cohort 拆解 + 弹性曲线 + 热力图互证，单一证据不下结论。反事实干预：选 5% 切片在第 5.5 个月发定向挽留触达（低成本），测 30 天留存差。若干预有效且集中在某假设对应的 cohort，即锁定根因，再设计根治方案。

</details>
**追问：** 挽留触达的度量你会看什么？

### XE14 · 挑战
**题干：** 新版排序上线后 CTR 掉了 15%。你的排查顺序是什么？
**及格要点：** 先查工程再查算法——是否干净全量、服务延迟有没有变；再做切片定位。
**优秀要点：** 四步完整：① 工程确认（模型是否真的 100% 生效、延迟/超时变化）；② 切片（行业/国家/浏览器/时段，找 15% 集中在哪）；③ 消融（位置偏差——点击位置分布变了没；新内容偏好 vs 个性化失效）；④ 排序诊断（近期批次上算 NDCG、看区分度是否塌了、tie-break 规则是否主导）；决策框架：回退 vs 并行对比测试，以"实验平台可信度"为第一优先。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #57，MIT）：**

> First, instrument: did the model roll out cleanly to 100%? Did server latency shift? Second, segmentation: where is it 15%? Vertical, country, browser, time-of-day? Third, ablations: did the click position change (position bias)? Did the model prefer new content (novelty) or did personalization break (skew in feature embedding)? Fourth, ranking diagnostics: side-by-side NDCG on a recent batch; check if rankings are still differentiating or if a tie-breaking rule now dominates. Decide: ship rollback vs side-by-side test.

**中文参考答案：**

> 第一步先查仪表而不是算法：模型是不是干净地全量生效了（有没有部分节点还跑旧版）？服务端延迟有没有变化（慢了会压 CTR，跟模型无关）？第二步切片：15% 是均匀掉还是集中在某个行业/国家/浏览器/时段？均匀掉指向系统性问题，集中掉指向局部 bug 或某类内容的问题。第三步消融归因：点击位置分布变了没（位置偏差——新排序把高 CTR 位置给了别的类目）；是模型偏爱新内容（新颖性偏好）还是个性化失效（特征 embedding 偏斜）；第四步排序诊断：在近期批次上并行算 NDCG，看区分度是否塌了、是否大量并列由 tie-break 规则决定（等于随机排序）。决策：回退 vs 双排序并行对比测试——优先保实验平台可信度，别让这次事故污染后续所有实验的信任。

</details>
**追问：** 怎么在不破坏实验平台信任的前提下发修复版？

### XE15 · 挑战
**题干：** 要把商品自动分类到类目和子类目，你的方案是什么？（Amazon 业务案例题型）
**及格要点：** 两阶段思路——LLM 冷启动生成候选分类 + 人工标注训练监督分类器；有难例转人工的回路。
**优秀要点：** 完整设计：① 层次化零样本/少样本 LLM 生成候选类目 + 检索已有 taxonomy 辅助；② 每层训练监督分类器（可用 embedding 特征）；③ 主动学习——不确定样本路由人工，人工结果回流；④ 评测：held-out 标注集上算误分率，线上对现有启发式规则 A/B；⑤ 能答多标签扩展和"人类还没标过的新类目怎么办"。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #58，MIT）：**

> Two-stage approach: (1) hierarchical zero-shot or few-shot LLM-based candidate category generation with retrieval over the existing taxonomy; (2) supervised classifier trained on human-labeled examples at each level, optionally using embedding features. Maintain a feedback loop for ambiguous cases routed to humans (active learning). Evaluate against held-out labeled set; A/B online against current heuristic on the share-of-misclassification metric.

**中文参考答案：**

> 两阶段：第一阶段用 LLM 做层次化的零样本/少样本候选类目生成，配合对现有类目树的检索（把类目定义和示例召回进上下文），覆盖长尾无需标注；第二阶段在每个层级训练监督分类器（人工标注样本 + embedding 特征），换更低时延成本。中间是主动学习回路：分类器低置信/LLM 与分类器分歧的难例路由给人工，标注结果回流训练集。评测：held-out 标注集上按层级算误分率（子类目误分率天然高于父类目，分开报）；线上与现行启发式规则 A/B，看总体误分份额和各品类切片。扩展性：多标签场景把 softmax 换成多个二分类头或按标签层级分解；新类目（人工未标）靠 LLM 阶段的开放词表发现，聚出的候选走人工确认后进 taxonomy。

</details>
**追问：** 多标签怎么扩展？人类还没标过的新类目怎么处理？

### XE16 · 挑战 ｜ Reported 真题
**题干：** 一个 LLM agent 代表用户执行动作（下单、发邮件、改配置）。怎么度量它"执行对了"？你的评测体系是什么？（Google DeepMind 实问）
**及格要点：** 区分"理解对了"和"执行对了"——参数抽取正确 + 动作选择正确 + 执行结果正确是三件事；有任务级成功率的概念。
**优秀要点：** 分层指标 + 分层手段：意图/动作选择准确率（离线标注集）、参数填充准确率（槽位级）、执行成功率（沙箱重放）、后果指标（用户撤销率、投诉、回滚）；危险动作单独建金丝雀集（不可逆动作的错误率目标是 0，必须 human-in-the-loop 门禁）；线上用"执行后被用户撤销/立即更正"的代理信号；对比两种度量方案（人工审计 vs 沙箱自动重放）并说明适用边界。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Google DeepMind 实问，Hard。landed.jobs 答案页仅给出结构提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify what "correctly executes" means for this product (action selection, parameters, consequences); ② Compare credible measurement approaches and state the decision criteria; ③ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 先定义"执行正确"的三个层次：动作选择对（用户要发邮件，agent 没去下单）、参数对（收件人、金额、时间没填错）、结果可接受（执行后用户没撤销）。度量分四层：① 离线标注集上的动作选择准确率与槽位级参数准确率（分开报——参数错比选错动作更隐蔽）；② 沙箱重放执行成功率（真实 API 的 mock 环境跑全流程）；③ 线上后果代理信号：执行后 5 分钟内用户撤销率、立即更正率、投诉率；④ 不可逆危险动作（支付、删数据、外发邮件）单建金丝雀集，错误率容限是 0，评测不过就不给执行权限，必须 human-in-the-loop 确认。度量方案对比：人工审计贵但能评"结果可接受"这种主观层；沙箱自动重放便宜可回归但评不了真实世界副作用——所以离线用沙箱、线上用后果信号、季度做人工审计。什么证据会改方案：如果撤销率与离线指标长期不一致，说明沙箱分布已失真，需要重建。

</details>
**追问：** 不可逆动作的评测和门禁怎么设计？

### XE17 · 进阶 ｜ Reported 真题 ｜ 变体：E10
**题干：** 你会怎么度量一个生成式 AI 产品的成功？（Microsoft 实问）
**及格要点：** 有分层指标意识（任务完成/质量/护栏）；离线 + 线上双轨；不是只报"使用量"。
**优秀要点：** 指标体系完整且说清因果链——北极星（用户任务完成率）← 质量指标（正确率/幻觉率/引用可核验率）← 行为指标（采纳率、留存、复访）；护栏（拒答率、成本、延迟、投诉）；生成式特有的坑：使用量会骗人（尝鲜流量）、质量没有客观金标时用 judge + 人工锚定；验证闭环：上线前后各留对照、按季度回看长期指标；明确说"什么证据说明它失败了"。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Microsoft 实问，Medium。landed.jobs 答案页给出 4 步结构提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify what "success" means for this product; ② Compare credible metric systems and state the decision criteria; ③ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 第一层定"成功"的本体：生成式产品的成功是"用户带着任务来，任务被更好/更快/更便宜地解决"，不是"生成次数"。指标体系三层 + 因果链：北极星——任务完成率（用后续行为或抽检定义"完成"）；支撑——质量（正确率、幻觉率、引用可核验率）、采纳率（输出被用户保留/修改后保留的比例）、成本延迟；护栏——拒答率、投诉率、有害输出率。生成式特有的两个坑：① 使用量会骗人——尝鲜流量退潮后留存才是真信号，看第 8 周留存；② 质量无金标——LLM-judge 上量 + 人工锚定子集校准。验证：灰度对照测增量、季度回看长期指标。失败的判据写死：护栏恶化或长期留存低于对照，任一触发即回退重审。

</details>
**追问：** 使用量涨但留存平，你怎么判断这个产品算不算成功？

### XE18 · 挑战
**题干：** 推理模型（o 系列 / R1 类）在评测上和普通对话模型有什么本质不同？你的评测方法要改什么？
**及格要点：** 知道三个差异：延迟成本不对称（贵 10-30 倍）、可见输出只是内部推理的摘要、精确匹配类指标会虚高。
**优秀要点：** 方法论调整完整：① 能力对比换推理特化基准（MATH、FrontierMath、GPQA Diamond、AIME）；② 成功率按成本归一（不是"答对了"而是"多少钱答对的"）；③ 加推理轨迹分析（采样 CoT 判逻辑一致性）；④ 监控过度自信——推理模型在中间步幻觉时失败得更沉默；量级感：被动基准已饱和，区分度要靠 harder held-out。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/llm-and-ml-concepts.md #46，MIT）：**

> Reasoning models (o1, o3, DeepSeek-R1) generate internal chain-of-thought tokens then a summary. Three eval differences: (1) latency/cost asymmetric: reasoning models are 10-30x more expensive and slow; normalize by "task cost" not "answer correctness". (2) Output semantics: the visible answer is much shorter than the work behind it; metrics like "verbosity" lose meaning. (3) Some metrics (exact-match GSM8K) inflate because the model has more compute to find the right answer; passive benchmarks become saturated. Senior recipe: (a) use held-out reasoning-specific benchmarks (MATH, FrontierMath, GPQA Diamond, AIME) for capability comparison; (b) re-evaluate with cost-normalized success rate; (c) add reasoning-trace analyses (model's CoT sampled and judged for logical consistency); (d) monitor for overconfidence: reasoning models fail silently when they hallucinate a wrong intermediate.

**中文参考答案：**

> 推理模型（o1/o3、DeepSeek-R1）先生成内部思维链 token 再给摘要。评测的三个差异：① 延迟与成本不对称——推理模型贵 10-30 倍且慢，指标要按"单位任务成本"归一，不能只看"答对了没有"；② 输出语义变了——可见答案远短于背后的工作量，"冗长度"这类指标失去意义；③ 部分指标虚高——精确匹配类（GSM8K exact-match）因为模型有更多算力去凑答案而膨胀，被动基准大面积饱和。资深配方：(a) 能力对比换 held-out 的推理特化基准（MATH、FrontierMath、GPQA Diamond、AIME）；(b) 全部换算成成本归一成功率；(c) 加推理轨迹分析——采样 CoT 判逻辑一致性，防止"答案对但推理链是错的"；(d) 盯过度自信：推理模型在中间步幻觉时失败得非常沉默——最终答案看起来同样笃定，所以要监控中间步质量代理指标。

</details>
**追问：** 什么是"推理税"？思维链什么时候反而有害？

---

## D. 商业判断（B · 4 题）

### XB01 · 进阶 ｜ 变体：B06
**题干：** 推理成本要在当前规模上砍 60%，你的完整方案是什么？
**及格要点：** 至少给出三条正交手段：模型分级路由、缓存（精确/语义）、限制输出与上下文。
**优秀要点：** 混合架构完整：短简单 query 路由到本地小模型（如 phi-3.5-mini）、长上下文与高风险 query 走托管大模型 + 请求级缓存 + KV-cache 复用；语义缓存（query embedding 找历史高相似命中直接回缓存答案）；tokens-per-minute 预算告警；成本节省按客户可见（可观测性把省钱显性化）；说清何时失效（语义缓存把"相似但不等价"的 query 错误命中，质量风险要有兜底抽检）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/data-and-applied-science.md #37，MIT）：**

> Architect: simple and short queries routed to phi-3.5-mini on local GPU; long-context and high-stakes queries routed to a hosted model with request-level cache + KV-cache reuse. Implement a semantic cache: embedding top-k similarity vs prior queries; on hit, return the cached answer; on miss, escalate. Budget alerts via tokens-per-minute. Surface observability so savings are visible per customer.

**中文参考答案：**

> 架构分流：简单短查询路由到本地 GPU 上的小模型（phi-3.5-mini 级），长上下文和高风险查询走托管旗舰模型，配请求级缓存 + KV-cache 前缀复用。语义缓存：对 query 做 embedding，和历史 query 算 top-k 相似度，超阈值直接返回缓存答案，未命中才升级到模型。预算侧：tokens-per-minute 告警 + 按客户配额。把成本可观测性做出来：每个客户能看见自己省了多少钱——省下的钱要显性化才有商业说服力。风险兜底：语义缓存有"相似但不等价"的错配风险（金额、日期一词之差），命中规则要设硬槽位一致（数字、实体必须精确匹配），并抽检缓存命中率的质量。其他杠杆叠加：裁剪上下文、限制输出长度、循环轮次上限——多层叠起来 60% 才现实。

</details>
**追问：** 这个方案什么时候会失效？质量-成本 Pareto 怎么权衡？

### XB02 · 挑战
**题干：** 客户委托你评估"该不该上 ML"——像咨询顾问一样给出从商业框架到落地方案的完整结构。（BCG X / QuantumBlack 案例题型）
**及格要点：** 有商业框架（issue tree / 假设树）+ 落地路径（数据现状 → 治理约束 → 窄用例 → 交付 → 度量 → 扩展），不是只谈模型。
**优秀要点：** 两层结构咬合：咨询层——where-to-play（哪个业务环节杠杆最大）、价值假设树（收益来源拆解到可估量）；部署层——评估数据就绪度、定义治理与合规约束（监管行业先行）、选一个 6 周能交付的窄用例、上线度量、再扩展；能答"最小可行试点（MVP）是什么"——单流程、金标准可判、人工兜底可回退。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #66，MIT）：**

> Standard consulting casing structure (issue tree, hypothesis tree, where-to-play) layered with the FDE deployment loop: assess data → define governance constraints → pick a tight use case → ship in 6 weeks → measure → expand. The case wants to see that you can both frame the business AND scope a deliverable ML system.

**中文参考答案：**

> 双层结构。咨询层：issue tree 把"该不该上 ML"拆成"哪里有可量化的痛（人工成本/质量损失/速度瓶颈）→ 数据是否就绪 → 竞争紧迫性"；假设树给出价值假设（如"自动分类能省 60% 人工审核工时"）并倒推验证路径；where-to-play 选杠杆最大且 6 周能验证的环节。部署层按 FDE 循环走：① 数据就绪度评估（有没有标注、量够不够、质量如何）；② 治理约束前置（监管行业先画红线：可解释性、人审、数据出境）；③ 选窄用例——单一流程、结果可判对错、人工可兜底；④ 6 周交付（不是 6 个月——周期本身就是说服客户的关键变量）；⑤ 上线度量（对照人工基线的准确率 + 工时节省 + 错误代价）；⑥ 达标后横向扩展到相邻流程。MVP 定义：一个流程、金标准可判、随时可回退人工——三者缺一就不叫试点。

</details>
**追问：** 最小可行试点是什么？

### XB03 · 挑战
**题干：** 讲一次你从多个客户/案例里识别出共性模式、并因此改变团队工作方式的事。
**及格要点：** 有具体模式（不是"我总结了很多经验"）；说清建了什么、改了什么、结果如何。
**优秀要点：** 三段式扎实：模式命名具体（如"所有受监管客户第 2 周必然要 X"）→ 产出具体（checklist、参考架构、模板）→ 结果可量（部署周期缩短、复购、NPS）；能回答"为什么之前没人做"（信息分散在个人脑中、没有跨案例复盘机制——你建立了机制而不只是个人洞察）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #59，MIT）：**

> Name the pattern (e.g., "every regulated customer wanted X within week 2"). Name what you built (e.g., a checklist + a reference architecture). Name the measurable outcome.

**中文参考答案：**

> 三段式：① 模式——服务第 5 个受监管行业客户时发现，他们无一例外在部署第 2 周提出合规审查材料需求（数据流向说明、审计日志、模型行为文档），每次都打乱排期；② 产出——把散在 5 次项目里的应答整理成"合规就绪包"：一份 checklist（第 0 周就发给客户提前准备）、一套参考架构（审计日志与权限的标准接法）、一份模型行为文档模板；③ 结果——后续受监管客户的部署周期从平均 8 周压到 5.5 周，合规相关返工从每项目 3 次降到 0.5 次，该包成为团队标准交付物。为什么之前没人做：每个项目经理只见过自己的 1-2 个案例，模式只存在于集体经验的盲区——我做的其实是建立了跨案例复盘的机制（季度模式提炼会），这个机制后来还产出过另外两个标准化资产。

</details>
**追问：** 为什么其他人没有更早做这件事？

### XB04 · 进阶
**题干：** 你入职后的前 30/60/90 天计划是什么？（AI 产品/部署类岗位）
**及格要点：** 三阶段有递进（观察 → 带做 → 主导）；每阶段有可量产出，不是"熟悉业务"这种虚目标。
**优秀要点：** 30 天：跟 3-5 个项目全程、产出平台/流程的个人地图并标出疑点；60 天：在资深影子下独立端到端负责一个项目；90 天：主导一个项目交付 + 提出一个流程改进并落地；每个阶段绑定可测产出（地图文档、项目指标、改进前后对比）；能答" ramp 期最大风险是什么"（过早下结论改东西——前 30 天只观察不动手是纪律）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #62，MIT）：**

> 30: shadow 3-5 deployments, write a personal map of the platform. 60: own one end-to-end deployment with a senior shadow. 90: lead a deployment, surface a process improvement. Tie each phase to a measurable output.

**中文参考答案：**

> 30 天（观察 + 建模）：全程跟 3-5 个项目，产出一份个人版"平台与流程地图"——客户旅程、内部工具链、决策点、已知的坑，并标注疑点清单；纪律是只观察不动手改。60 天（带保险带做）：在资深同事影子支持下独立端到端负责一个项目，指标与团队基线对齐；把 30 天地图里的疑点挑 2 个验证真伪。90 天（主导 + 反哺）：独立主导一个项目交付；提出至少一个流程改进并落地（来源通常是 30 天疑点清单中被验证的那几条），给出改进前后的量化对比（周期、返工率）。Ramp 期最大风险：过早下结论——新人在第 3 周觉得"这流程明显有问题"然后动手改，大概率踩的是自己还没理解的隐性约束。所以前 30 天不动手是设计出来的纪律，不是谦虚姿态。

</details>
**追问：** 你 ramp 期最大的风险是什么？

---

## E. 伦理与合规（S · 6 题）

### XS01 · 挑战
**题干：** 一场关于 AI 安全的辩论：部署场景模糊、安全与商业冲突时，你怎么把权衡讲清楚并守住立场？
**及格要点：** 能把风险说具体（不是"AI 有风险"，而是"这个模型不加过滤会被用来生成 X"）；有缓解措施和残余风险的概念。
**优秀要点：** 四段论：风险显式化（具体滥用路径）→ 缓解措施（输出分类器拦高风险类内容）→ 残余风险量化（误拦率 + 漏拦率的容忍度）→ 观测到问题时的回退；核心观点：目标不是"不计代价求安全"，而是**让权衡变得可读**（legible）——哪怕结论是继续上，也要让决策成本透明；能顶住"客户说安全措施伤质量"的追问（用误拦率数据说话、给分级方案而不是全撤）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #46，MIT）：**

> State the risk explicitly (e.g., "the model can be misused to generate X if we don't add filtering"). State the mitigation (e.g., "we put an output classifier in front of risky content types"). State the residual risk (false positives, false negatives). State the rollback if observed. The point is not to be "safe at all costs", it's to make the trade-off legible.

**中文参考答案：**

> 四段论走完：① 风险显式化——"不加输出过滤，这个模型会被用来批量生成 X 类内容"，具体到滥用路径而不是抽象的"有风险"；② 缓解措施——对高风险内容类型前置输出分类器，写清拦截哪几类、阈值多少；③ 残余风险——误拦（误伤正常用户）率和漏拦率的估计值，以及各自的容忍度（误拦 2% 可以接受吗？漏拦呢？）；④ 回退预案——观测到漏拦案例后多快能收紧阈值、要不要一键下线。核心观点：目标不是"不计代价求安全"，而是让权衡可读——把"继续上"的成本透明地摆在决策桌上，让拍板的人知道自己在为什么买单。被客户挑战"安全措施伤质量"时：拿误拦率数据说话（误拦的是哪类、占比多少），给分级方案（高风险场景保留过滤、低风险场景放宽），而不是全撤防线。

</details>
**追问：** 客户说你们的安全措施伤害了产出质量，你怎么办？

### XS02 · 挑战
**题干：** 你工作中是怎么考虑 AI 安全权衡的？（OpenAI Mission Fit 实题型）——给出一个你为安全付出过真实代价的具体决定。
**及格要点：** 有具体案例（不是价值观陈述）；说出守住安全付出的代价（延期、砍 scope、丢客户）。
**优秀要点：** 案例真实且"疼"——如拒绝上线一个评测不充分的自主性功能，付出了延期和客诉；点出"抽象的安全"通常失效，多数安全胜利是对**具体功能入口的具体拒绝**；价值观可持续的证明（不是第一次这么做，是一贯如此）；避开把安全当营销话术的陷阱。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/frontier-ai-labs.md #7，MIT）：**

> Name a concrete shipping decision you held the line on (e.g. refused to launch an evals-light autonomy feature); describe the invisible cost you accepted (delays, scope cuts, opt-outs for high-risk customers); be explicit that "safety in the abstract" usually fails, most safety wins are specific refusals of specific affordances. Avoid the trap of treating safety as a marketing line.

**中文参考答案：**

> 讲一个真实的决定：agent 产品原计划上线"自动执行"档位，上线前评测显示某类边界输入下误执行率没达到门槛，我顶着销售压力推迟了两周、砍掉了首发的一个自动化档位——代价是延期、一个大客户的首单延后、内部有人不爽。讲清楚当时的推理：误执行是**不可逆动作**，评测不过就是不过，没有"先上再修"的选项。关键认知：「抽象的安全」几乎总是失效——"我们重视安全"这句话挡不住任何具体事故；真正的安全胜利都是对具体功能入口的具体拒绝：拒掉这一个按钮、这一个自动权限、这一类免确认路径。可持续性证明：这不是孤例——再补一个更早的类似决定（比如主动把高风险客户移出某功能白名单），说明这不是面试话术而是一贯行为模式。最后主动点题：安全不该出现在营销文案里作为卖点，它的正确位置是发布门槛。

</details>
**追问：** 讲一次你出于伦理原因反对某个技术决定。

### XS03 · 挑战
**题干：** 面试官在文化轮问你：安全与负责任部署在你的工作里占什么位置？——你要拿出什么证据？
**及格要点：** 有 2-3 个把安全/伦理置于交付速度之前的实例；不是临时表态。
**优秀要点：** 实例覆盖"慢但安全的选择、提前提出的隐患、拒绝过的用例"三种形态；证据有细节（当时的冲突、你说的原话、结果）；关键信号：安全思维是**工作方式的内置部分**（评测先行、红线前置）而不是事后补丁；能答"客户非要上明显有风险的用例怎么办"（给替代方案 + 书面记录风险 + 分级拒绝）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #64，MIT）：**

> Have 2-3 examples where you put safety/ethics ahead of velocity (e.g. chose a slower-but-safer deployment, raised a concern early, refused a use case). Show durability, this is not the first time.

**中文参考答案：**

> 准备 2-3 个不同形态的实例，覆盖三种类型：① 选了更慢但更安全的方案（如用带审计日志的自建管道替代快两周的第三方捷径）；② 提前提出的隐患（上线前三周就写了某功能被滥用的风险备忘，后来果真拦截了一起）；③ 拒绝过的用例（客户想把客服 agent 用于给用户做投资建议，拒绝了，给出合规的替代边界——只答产品事实不给建议）。每个实例都要有当时的冲突细节和你说过的原话，光有结论没有过程会像背稿。核心信号是"内置性"：安全在你的流程里是前置的（评测先于排期、红线写进需求文档第一页），不是发布前补的检查项。追问"客户非要上有风险的用例"：先给替代方案（降级设计、加人审），客户仍坚持则书面记录风险与责任边界，触及红线的用例直接拒绝并解释为什么不卖——**有些单子不接本身就是产品决策**。

</details>
**追问：** 客户想上线一个明显有风险的用例，你怎么处理？

### XS04 · 挑战 ｜ Reported 真题
**题干：** 消费级产品里的生成式 AI 安全，你的整体方法论是什么？（Google / Anthropic / OpenAI 实问）
**及格要点：** 覆盖输入/输出两侧的防线（内容过滤、护栏模型）；有分场景的风险等级意识（面向未成年人 vs 成人）。
**优秀要点：** 分层防御体系：① 输入侧——提示注入检测、意图分类前置；② 生成侧——护栏模型拦有害类别、年龄适宜性分级；③ 输出侧——高风险动作（外部链接、支付、隐私数据）强制确认；④ 运行侧——可停止（一键断流）、可审计（全轨迹日志）；⑤ 评测侧——红队集 + 上线后对抗样本回流；度量齐备：有害输出率、误拦率、未成年人暴露率各自的阈值与告警；明确残余风险的接受逻辑和监管基线（《生成式人工智能服务管理暂行办法》类合规框架）。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：Google / Anthropic / OpenAI 实问，Hard。landed.jobs 答案页仅给出结构提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify objective, users, constraints, and failure tolerance; ② Cover layered defenses with metrics; ③ Compare credible alternatives and state the decision criteria; ④ Finish with validation, monitoring, and what would change the decision.

**中文参考答案（本卷按该结构编译）：**

> 先分用户与失败容忍度：消费级产品的约束是用户不可培训、未成年人在场、事故直接上新闻——失败容忍度按"不可逆伤害"排序。分层防御：① 输入侧——提示注入与越狱检测、意图前置分类；② 生成侧——护栏模型对有害类别（自伤、暴力、违法指导）分级拦截，拦截不是二元的，按年龄档与场景档分级；③ 输出侧——高风险动作（给外部链接、引导支付、索取隐私）强制用户确认；④ 运行侧——任何会话可一键停止、全轨迹可审计；⑤ 评测侧——常备红队集、上线后的对抗样本每周回流进集。指标三件套：有害输出率（漏拦）、误拦率（伤害正常体验）、未成年人暴露率，各有阈值与告警线，任一恶化触发收紧。方案对比与决策标准：自建护栏模型 vs 供应商方案，按"可调阈值粒度 + 审计能力 + 成本"三判据选。残余风险：不可能归零，接受逻辑是"不可逆伤害类残余风险必须趋零，可逆体验类风险可按数据权衡"。监管基线对齐所在地生成式 AI 服务管理办法。什么会改变决定：出现新型攻击向量（红队或线上发现）→ 48 小时内重评估防线配置。

</details>
**追问：** 误拦率涨了影响体验，你怎么平衡？

### XS05 · 挑战
**题干：** 讲一次你不同意客户、并且坚持住了立场的经历——尤其是拒绝了一个会伤可靠性/安全性的做法。
**及格要点：** 有真实案例；说清拒绝的理由（成本 vs 风险怎么框的）和给出的替代方案；关系没有破裂。
**优秀要点：** 结构完整：客户要的 workaround 为什么有害（具体风险路径）→ 你怎么把成本与风险摆到同一张表上（量化对比而不是立场对抗）→ 替代方案是什么（不是光说不行）→ 结果（短期代价 + 长期信任）；诚实处理"坚持住"的代价（可能丢了这个单或被升级到上级）；点出关键：让数据替你说话，你负责提供选项和后果，客户拍板但知情。
<details><summary>完整参考答案（中英对照）</summary>

**EN（banks/fde-product-and-gtm.md #58，MIT）：**

> Pick a case where you refused a workaround that would have hurt reliability. Show how you framed the cost-vs-risk and the alternative proposal you offered. Show the outcome.

**中文参考答案：**

> 案例：客户为了赶内部上线日，要求跳过回归评测直接放量一个未验证的模型版本。框架：不说"不行"，摆一张表——方案 A（跳过评测直接上）：省 3 天，风险是历史回归 case 里约 12% 的失败类型可能复发，其中包含一次造成过客诉的幻觉引用；方案 B（压缩评测：全量砍到金丝雀集 50 条 + 高风险切片）：多花 1 天，覆盖 80% 已知风险；方案 C（原计划全量回归）：多 3 天，覆盖最全。我推荐 B，附上每个方案的失败代价换算（B 方案复发风险约 2% vs A 的 12%）。结果：客户选了 B，上线后没出事故；一个月后他们主动把全量回归写进了自己的发布流程。关系处理：客户采购负责人一开始要求"无条件跳过"并升级到我上级，我把那张表发给双方——让数字说话、我提供选项和后果，决策权留给客户但保证知情。这次"坚持"短期多花了一天，长期换来客户把我们的评测标准当成了他们自己的标准。

</details>
**追问：** 客户当时的反应是什么？

### XS06 · 挑战 ｜ Reported 真题
**题干：** 有人抛出一个挑衅性论断——"未来 5 年 AI 会取代大部分知识工作者"。你怎么回应？（OpenAI 实问）
**及格要点：** 不站队情绪，能拆解论断：哪些部分可检验、哪些是定义模糊的修辞；有自己的立场且给出依据。
**优秀要点：** 拆解为可讨论的结构：① "取代"的定义（任务替代 vs 岗位消失 vs 岗位重构——经济史上技术多为重构）；② 时间尺度的检验方式（任务级自动化率的可测趋势 vs 岗位统计的滞后性）；③ 二阶效应（新岗位、成本曲线下降带来的需求扩张——Jevons 悖论式）；④ 落到 PM 视角：不管宏观结论如何，产品设计都该按"人机协作 + 判断权在人"来做，这既是风险对冲也是当下最优解；姿态：有立场地讨论而不是和稀泥，但承认不确定性来源。
<details><summary>完整参考答案（中英对照）</summary>

**EN（Reported 真题：OpenAI 实问，Hard。landed.jobs 答案页未给出内容提示，成文答案为本卷编译）：**

> Structure hint (from landed.jobs): ① Clarify the claim; ② Compare credible alternatives and state the decision criteria; ③ Finish with validation, monitoring, and what would change the view.

**中文参考答案（本卷编译）：**

> 先拆"取代"这个词的三种含义：任务替代（已经在发生——草稿、摘要、初筛）、岗位消失（历史上罕见——ATM 没消灭柜员，改变了柜员的工作）、岗位重构（最可能的路径：判断密集型任务留给人，执行密集型给 AI）。再拆检验方式：任务级自动化率是可测的先行趋势，岗位统计是滞后指标，拿滞后指标反驳先行趋势是常见错误。二阶效应：执行成本暴跌通常扩张总需求（Jevons 悖论——蒸汽机效率提升后煤消耗量反而上升），知识工作的"总盘子"可能变大。我的立场：5 年内大部分知识工作会被深度重构、但"取代大部分岗位"缺乏经济学依据；同时承认最大的不确定性在二阶效应的速度。落到 PM 本行：无论宏观结论如何，当下的正确设计都是"人机协作 + 判断权在人"——这既是对不确定性的对冲，也是当前技术边界下的最优解。什么证据会让我改观点：如果任务自动化率的提升不再伴随新任务类别的产生（净创造停滞），我会转向悲观一侧。

</details>
**追问：** 如果对方步步紧逼要求你给出明确的百分比预测，你怎么接？

---

## 附：使用说明

1. **何时用本卷**：主卷（question-bank.md）一轮测完后的二测；或用户主动要求"更难 / 更贴近大厂真实面试"。首次测评默认仍用主卷。
2. **选题规则**：沿用 SKILL.md 的自适应规则；维度内先问基础（若有）→ 按得分升降难度。本卷基础题仅 4 道（XT04 / XP09 / XP10 + 追问储备），进阶/挑战为主，被测评者得分预期应对照"挑战题答对 = 4 分起步"校准。
3. **变体去重**：标了「变体：XXn」的题与主卷同主题。跨轮次选题时，若上一轮已问过主卷对应题，本轮可选用扩展卷变体（考察深度是否随学习提升）；同一轮内主卷与扩展卷变体不得同现。
4. **评分纪律不变**：及格/优秀要点仍是打分锚点；双语完整答案是给评分者做判断校准的，**不泄露给被测评者**。
5. **Reported 真题的诚实边界**：10 道 Reported 题的题干与提问公司来自 landed.jobs 的候选人报告（可信度标注 Reported），但答案页仅有结构提示——本卷标注为"编译"的中文答案是编者按该结构撰写的参考，不是官方答案，点评时应以要点覆盖度打分而不是对照"标准答案"。
