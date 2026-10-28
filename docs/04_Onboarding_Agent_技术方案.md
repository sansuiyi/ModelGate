# ModelGate 合同抽取 Onboarding Agent 技术方案（v2 · 需求驱动选型）

> **v2 修订要点**：v1 隐含假设"合约里写了模型名"，只做抽取 + 校验。真实合约（见 `customer_contracts/` 与 `backend/data/sample_contracts/` 共 9 份）**全部不写模型名**，只写"允许/禁止哪些供应商 + 延迟/隐私/成本/上下文等业务需求"。
> 因此 Agent 的核心职责不是"抄模型名"，而是**把业务需求翻译成模型选型**。这是纯语义推理，规则表达不出来——也正是 ReAct 不可替代的地方。
>
> 原则：**不碰路由分类器（微调模型）与请求链路**；工具只提供事实（能力查询、可行性统计），不做选型决策；选型由 LLM 推理。

---

## 一、真实合约的形态（证据）

| 合约 | 是否写模型名 | 写了什么 |
|---|---|---|
| 01 华康医疗 智能分诊 | ❌ | 允许 DeepSeek/GLM，禁 OpenAI/Anthropic/Google；CN 境内；分诊 1200ms、摘要 5000ms、会诊 10000ms；成本敏感高 |
| 05 法盾律所 法律文书 | ❌ | 允许 DeepSeek/GLM，禁境外；CN 境内；检索 2000ms、起草 6000ms、策略 10000ms；质量优先、成本敏感低 |
| 08 Helios Energy | ❌ | 允许 Anthropic/OpenAI，禁 Google、禁中国供应商；EU-only；告警 2000ms、诊断 10000ms（质量优先） |
| samsung_care_plus | ❌ | 允许 Anthropic/OpenAI/Google，禁中国供应商；US-only；Tier1 1500/3000/4000ms（成本优先）、Tier2 3000/8000ms（质量优先）、Galaxy AI 类禁用轻量模型 |

**结论**：合约给的是**约束 + 需求**，模型选型必须由 Agent 推导。

### 这带来三个 v1 没覆盖的硬需求

1. **需求 → 能力的映射**：`1200ms 内返回` → 筛选 `avg_latency_ms ≤ 1200` 的合规模型；`40 页文档摘要` → 筛选 `max_context ≥ 100k`；`成本敏感高` → 优先低价模型。
2. **可行性预判**：约束可能把某档清空。例如"仅 CN 境内 + 仅 DeepSeek/GLM"在当前目录下 **simple/complex 档没有任何 CN 模型**——这是真实的能力缺口，必须在 onboarding 时发现并告警，而不是等请求进来才暴露。
3. **每档独立的需求**：合约常给**分档**需求（简单 1200ms / 中等 5000ms / 复杂 10000ms + 质量优先）。选型必须**按档分别对齐**，而不是用一个全局 latency 应付。

---

## 二、两种合约模式（Agent 必须先判断）

```
模式 A：合约显式点名供应商/模型
  例：允许 Anthropic、OpenAI → 直接在允许集合里挑模型，重点是「校验不违约」
  路径：抽约束 → 列表验证 → 选型（集合已很小） → 自检 → finalize

模式 B：合约只写需求（本项目主流）
  例：1200ms 内、成本优先、CN 境内、仅 DeepSeek/GLM
  路径：抽约束 → 抽需求（按档） → 能力查询 → 逐档匹配 → 权衡冲突 → 自检 → finalize
```

模式 B 的核心循环：

```
① 抽约束（region / forbidden / allowed / privacy）
② 抽需求，按档拆：
     simple:  latency ≤ 1200ms, 成本优先
     medium:  latency ≤ 5000ms, 平衡
     complex: latency ≤ 10000ms, 质量优先、可用轻量模型否决
③ check_coverage → 知道「在约束下每档还剩几个可用模型」
④ list_models(tier=?, max_latency_ms=?, min_context_tokens=?, …) → 候选
⑤ 权衡：多个候选时按 objective / cost_sensitivity / 延迟余量排序 → 选 1–2 个
⑥ 某档为空 → 判断是「约束无解」还是「可跨档降级」→ 决定 warning 或降级
⑦ check_profile 自检 → 无未解释冲突 → finalize
```

---

## 三、为什么只有 ReAct 能做（对比规则方案）

| 环节 | 规则能写吗 | 说明 |
|---|---|---|
| 抽约束（禁哪些供应商） | 半能 | 关键词可覆盖，但"任何总部位于美国的供应商"这种表述必须语义理解 |
| 抽需求按档拆分 | ❌ | 合约是散文式的（"4.1.1 Standard queries within 1500ms at p95"），要理解哪句对应哪个档 |
| 需求 → 能力筛选 | 半能 | 筛选本身是数值比较（可代码化），但**"该筛哪几个维度、阈值取多少"**来自语义 |
| 多目标冲突权衡 | ❌ | "质量优先但成本敏感高"、"Galaxy AI 禁用轻量模型但要求 4000ms"——需要推理取舍 |
| 缺口归因与降级 | ❌ | 某档空了，是合约矛盾、目录不足、还是管理员禁用？处理方式完全不同 |

**这正是 v1 被质疑"规则也能做"的根因**：v1 只做校验+抄名字。v2 做的是**语义需求 → 数值筛选 → 冲突权衡**，规则表写不出来。

---

## 四、架构与文件落点

```
backend/
  agent/
    __init__.py
    contract_agent.py   # ReAct 主循环
    tools.py            # 事实工具（含能力过滤 + 可行性统计）
    prompts.py          # system prompt（双模式）+ 工具/finalize schema
  services/
    extractor.py        # 保留单次抽取（fallback / A-B 对比基准）
    router_engine.py    # 已抽出 _evaluate_candidates 复用
  routers/
    extraction.py       # /extract/react（已接入，失败回退单次）
  config.py             # REACT_MODEL
```

技术栈：OpenRouter `tools`（OpenAI 兼容 function calling）。不引入 LangGraph / LangChain —— 线性多轮循环，手写 40 行更清晰。

---

## 五、工具设计（5 个，全部只给事实）

### 1. `list_providers()`
返回环境全部 provider 名。用于确认合约提到的供应商是否真的存在于目录。

### 2. `list_models(...)` ⭐ 能力感知过滤器（v2 核心增强）

```python
list_models(
    tier=None,                 # simple / medium / complex
    provider=None,
    region=None,               # EU / US / CN
    max_latency_ms=None,       # 新增：延迟上限（对齐合约 latency 要求）
    min_context_tokens=None,   # 新增：最小上下文（对齐长文档需求）
    max_cost_per_m_input=None, # 新增：输入单价上限（对齐成本敏感度）
    sort_by=None,              # 新增：latency / cost / context
)
```

返回精简信息：`name / provider / tier / regions / avg_latency_ms / max_context / cost_per_m_input / cost_per_m_output / description`。

**为什么必须加这三个能力维度**：目录里已有 `avg_latency_ms`、`max_context`、`cost_per_m_input`（见 [provider_registry.py](../backend/services/provider_registry.py)），但 v1 的 `list_models` 没暴露，Agent 无法按"1200ms / 100k 上下文 / 低成本"去筛。

### 3. `get_model(name)`
单模型完整信息；不存在返回 `null`（防幻觉）。

### 4. `check_coverage(constraints)` ⭐ 新增：可行性统计

输入 `{region, forbidden_providers, allowed_providers}`，返回：

```json
{
  "tiers": {
    "simple":  {"available": ["gemini-2.0-flash","gpt-4o-mini","claude-haiku"], "count": 3},
    "medium":  {"available": ["gpt-4o","claude-sonnet","deepseek-v3"],     "count": 3},
    "complex": {"available": ["gemini-2.5-pro"],                            "count": 1}
  },
  "gaps": ["simple", "complex"]          // 在约束下无任何合规模型的档
}
```

**用途**：Agent 在动手选型前先知道"哪个档根本没有可选模型"，从而决定是**降级**还是**报缺口**。这是需求驱动模式最关键的前置事实。

### 5. `check_profile(draft)`
自检：给定草稿 profile，返回每档有效候选/淘汰明细/问题。**只报事实，不给修复建议**。

### 6. `finalize(profile)`（终止工具）
用 JSON schema 锁死输出结构，保证产出合法 `CustomerProfile`。

> 工具与决策的分界线：工具回答"目录里有什么、在约束下还剩什么、你的草稿有没有洞"；**选哪个、怎么权衡、要不要降级，全部由 LLM 推理**。

---

## 六、需求 → 选型的映射规则（Agent 的推理依据，写在 prompt 里）

| 合约需求表述 | 抽取为 | 选型动作 |
|---|---|---|
| "1200ms 内返回"（分诊） | simple 档 latency ≤ 1200 | `list_models(tier=simple, max_latency_ms=1200)` |
| "40 页文档摘要" | 长上下文需求 | `list_models(min_context_tokens=100000)` |
| "成本敏感度高，简单查询优先最低成本" | objective=low_cost，simple 档成本优先 | `list_models(tier=simple, sort_by=cost)` |
| "质量优先，成本次要" | objective=high_quality | complex 档优先高能力模型，可放宽延迟 |
| "禁用轻量/经济型模型" | complex 档排除 simple 档模型 | 只取 tier=complex |
| "禁止任何总部位于美国的供应商" | forbidden_providers 补全 US 供应商 | 结合 `list_providers` 逐个判定 |
| "必须在中国境内处理" | region=CN-only | `check_coverage` 看 CN 合规模型分布 |

**冲突时的优先级**（写进 prompt）：`合规(region/forbidden/allowed) > 隐私 > 质量偏好 > 延迟要求 > 成本`。合规永远不能为了延迟或成本让步。

---

## 七、ReAct 主循环与停止条件

```python
for _ in range(MAX_ITERS):        # MAX_ITERS = 14（v2 多一步 coverage 查询）
    resp = await openrouter_chat(messages, tools)
    if no tool_calls: raise / content fallback
    for tc in tool_calls:
        if tc.name == "finalize": return build_profile(tc.args)
        result = execute_tool(tc.name, tc.args)
        messages.append(tool_result)
```

| 停止条件 | 结果 |
|---|---|
| 调 `finalize` | 正常产出 |
| `MAX_ITERS` 耗尽 | 抛异常 → 调用方回退单次抽取 |
| LLM 报错/超时 | 回退单次抽取 |

**新增强制约束（写进 prompt）**：模式 B 下**必须先调 `check_coverage`**，再调 `list_models`——避免 Agent 凭空挑模型后才发现该档在约束下根本不可用。

---

## 八、一次需求驱动运行示例（华康医疗）

```
Thought: 合约允许 DeepSeek/GLM，禁 OpenAI/Anthropic/Google，须 CN 境内。
         先确认环境里的 provider 有哪些。
Action:  list_providers()
Obs:     ["anthropic","bytedance-seed","deepseek","google","openai"]

Thought: GLM(智谱) 不在目录里；CN 合规只剩 deepseek。先查约束下每档剩几个模型。
Action:  check_coverage({"region":"CN-only","allowed_providers":["deepseek"]})
Obs:     simple: 0, medium: 1(deepseek-v3), complex: 0, gaps: ["simple","complex"]

Thought: simple 档要求 1200ms 且成本优先，但 CN 合规无 simple 模型。
         检查 deepseek-v3 是否满足 medium 的 5000ms。
Action:  list_models(tier="medium", provider="deepseek")
Obs:     deepseek-v3: 600ms, max_context 128k, $0.30/$0.80

Thought: medium 可用。simple/complex 无合规模型 —— 这是目录缺口，不是合约矛盾。
         决策：simple 降级指向 deepseek-v3（600ms 满足 1200ms 延迟），
         complex 也指向 deepseek-v3，并生成两条 model_gap warning 说明缺口。
Action:  check_profile({...draft...})
Obs:     {"issues": []}   # 三档都有候选

Action:  finalize({
           constraints: {region:"CN-only", allowed_providers:["deepseek"]},
           routing_preferences: {simple:["deepseek-v3"], medium:["deepseek-v3"], complex:["deepseek-v3"]},
           warnings: [
             {"type":"model_gap","severity":"warning","tier":"simple",
              "message":"CN 合规模型中没有 simple 档；已降级用 deepseek-v3(600ms 满足 1200ms)"},
             {"type":"model_gap","severity":"warning","tier":"complex",
              "message":"CN 合规模型中没有 complex 档；复杂问题由 deepseek-v3 承载，质量风险需人工确认"}
           ],
           performance: {latency_target_ms: 1200, cost_sensitivity: "high"},
           ... })
```

> 注意：这个例子暴露了真实问题——**当前目录对"CN 境内 + 国产供应商"客户严重供给不足**。这既是 Agent 要报出的 gap，也是产品要补的模型供给（可接入 GLM/Qwen）。

---

## 九、每档需求的落库方式（零 schema 变更）

`CustomerPerformance` 只有单个 `latency_target_ms`，但合约常给分档延迟。v2 的处理：

- **选型时**：Agent 用分档延迟逐个筛选模型（不写进 profile）
- **落库时**：把分档需求与选型理由写进 `warnings`，结构化条目：

```json
{"type": "tier_requirement", "severity": "info", "tier": "simple",
 "message": "合约要求 1200ms/成本优先；选中 deepseek-v3(600ms, $0.30/M)"}
```

理由：避免为审计新增字段而动 `models.py`/`router_engine`（会牵扯请求链路）。若后续前端要展示分档 SLA，再单独立项加字段。

### finalize 兜底清洗策略（已实现）

LLM 仍可能给出违约或幻觉结果，`finalize` 落库前统一清洗：

| 情况 | 处理 |
|---|---|
| 模型不在目录（幻觉） | 剔除 |
| 供应商违反 forbidden / allowed | 剔除 |
| 区域不支持（region） | 剔除 |
| 某档清洗后为空 | 保留空列表 + 自动追加 `model_gap` warning |
| **模型档位 ≠ 所在档** | **保留**（需求驱动下允许跨档降级） |

> 最后一条很重要：华康这类"CN 境内 + 仅国产供应商"的客户，simple 档只能用 medium 档的 `deepseek-v3`。`router_engine._evaluate_candidates` 本身也不校验档位，因此跨档降级是合法且必要的，**不能按档位相等去清洗**（v1 的实现会误删合规模型、再塞回违约的默认模型）。

---

## 十、技术难点与对策

| 难点 | 对策 |
|---|---|
| **模式识别错误**（A/B 判错） | prompt 给出判别规则；若合约同时给供应商与需求，走 B（约束收缩后的需求匹配） |
| **筛选过度**导致某档为空 | 强制先 `check_coverage`；`list_models` 支持放宽阈值重试（Agent 自主放宽成本/延迟再查） |
| **合规红线被让位** | prompt 硬性优先级：合规 > 隐私 > 质量 > 延迟 > 成本；`check_profile` 兜底拦截违约模型 |
| **幻觉模型名** | `get_model` 校验 + `finalize` 二次清洗（`_sanitize_routing_preferences`） |
| **多步成本** | `REACT_MODEL` 可配便宜模型；模式 A 允许早停；MAX_ITERS 上限 |
| **context 膨胀** | `list_models` 只返回精简字段并强制过滤条件；`check_coverage` 只返回名字 |
| **不收敛** | MAX_ITERS + prompt 禁止重复相同查询 + 每轮必须有新信息 |
| **质量无法证明** | 用 9 份真实合约做评测集，对比 ReAct vs 单次抽取的「合规率 / 三档非空率 / 需求对齐率」 |

---

## 十一、与单次抽取的关系

- 原 `/extract`、`/extract/upload` 完全不动（单次 `extract_profile`）
- 新增 `/extract/react` 走 Agent，异常自动回退单次抽取
- `REACT_MODEL` 控制多步用的模型

**目的**：既能给简单合约留快速通道，也能用 A/B 对比证明 Agent 在需求驱动场景的增量。

---

## 十二、任务列表

| 任务 | 文件 | 内容 | 状态 |
|---|---|---|---|
| T1 | `services/router_engine.py` | 抽 `_evaluate_candidates` | ✅ 已完成 |
| T2 | `config.py` | `REACT_MODEL` | ✅ 已完成 |
| T3 | `agent/tools.py` | `list_models` 增加 `max_latency_ms / min_context_tokens / max_cost_per_m_input / sort_by` | ✅ 已完成 |
| T4 | `agent/tools.py` | 新增 `check_coverage()` | ✅ 已完成 |
| T5 | `agent/prompts.py` | 重写 system prompt：双模式 + 需求映射 + 合规优先级 | ✅ 已完成 |
| T6 | `agent/prompts.py` | 更新 `list_models` schema、新增 `check_coverage` schema | ✅ 已完成 |
| T7 | `agent/contract_agent.py` | 工具分发接入 `check_coverage`，MAX_ITERS 12→14 | ✅ 已完成 |
| T8 | 验证 | 工具单测 + 真实合约约束下的 coverage 报告 | ✅ 已完成 |
| T9 | `agent/contract_agent.py` | `finalize` 清洗改为「合规优先 + 允许跨档 + 剔除幻觉」，空档自动补 gap warning | ✅ 已完成 |
| T10 | `backend/tests/test_contract_agent.py` | unittest 测试（7 例，含脚本化 LLM 全链路） | ✅ 已完成 |

---

## 十三、验证方案与结果

1. **语法 / import**：`py_compile` 通过；`import backend.main` 正常（11 条路由）✅
2. **能力过滤正确性** ✅
   - `list_models(max_latency_ms=400)` → gemini-2.0-flash(300) / claude-haiku(350) / gpt-4o-mini(400)
   - `list_models(min_context_tokens=200000)` → 全部 ≥200k，按上下文降序
   - `list_models(max_cost_per_m_input=0.3)` → 全部 ≤$0.30/M
3. **coverage 正确性（用真实合约约束实测）** ✅

| 场景（对应真实合约） | constraints | 结果 | 结论 |
|---|---|---|---|
| 华康医疗 / 法盾律所 | CN-only + allowed(deepseek, glm) | simple 0、medium 1(deepseek-v3)、complex 0，gaps=[simple, complex] | **真实供给缺口**：CN 合规无 simple/complex 模型，且 GLM 不在目录 |
| Helios Energy | EU-only + allowed(anthropic, openai) + 禁 google/中国 | simple 2、medium 2、complex 0，gaps=[complex] | complex 档缺口（EU 合规 complex 模型为 0） |
| Samsung Care+ | US-only + allowed(anthropic, openai, google) + 禁中国 | simple 3、medium 2、complex 1，gaps=[] | 三档全覆盖 |

4. **回归**：`route()` 输出与重构前一致 ✅
5. **Agent 全链路单测（脚本化 LLM，无需 API key）** ✅ `python -m unittest backend.tests.test_contract_agent -v` → **7 passed**
   - 模式 B 全链路：list_providers → check_coverage → list_models → check_profile → finalize，工具结果正确回填（5 次 LLM 往返）
   - finalize 清洗：违约模型（gemini）与幻觉模型（claude-opus-4）被剔除，空档自动补 `model_gap`
   - 不收敛保护：达到 MAX_ITERS 抛 `RuntimeError`，由 `/extract/react` 回退单次抽取
6. **端到端（真实 LLM）**：⬜ 待联调 —— 当前 `.env` 的 `OPENROUTER_API_KEY` 返回 `401 AuthenticationError: The API key doesn't exist`，需更新有效 key 后执行

> 第 3 项验证直接证明了 v2 的必要性：**3 个真实客户里有 2 个存在能力缺口**，v1（只校验不选型）完全发现不了。

---

*本方案基于对 9 份真实合约、`provider_registry.py` 全量模型能力字段、`router_engine.py` 淘汰逻辑的分析编写。*
