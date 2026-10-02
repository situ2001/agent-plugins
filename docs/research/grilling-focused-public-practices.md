# Focused grilling 与同步文档的公开实践

检索日期：2026-10-02。对照本仓库 `skills/grilling-focused/SKILL.md` 与 `skills/grilling-focused-with-docs/SKILL.md`，核实公开源码和作者讨论。

本地 `grilling-focused` 按回答的后果筛选设计树：只保留需要用户判断、且会改变目标、范围、核心方案或验收条件的未决问题；事实通过调查解决，可逆的局部实现由代理判断。它保留原版 grilling 的依赖、frontier、推荐和确认规则。`grilling-focused-with-docs` 则是调用前者与 `domain-modeling` 的简短组合入口。

## 已公开实现

| 实现 | 与本地技能的对应 | 差异 |
| --- | --- | --- |
| [vvanagas / grill-me](https://github.com/vvanagas/agent-skills/blob/main/skills/grill-me/SKILL.md) | Method 3 只接纳会改变目标、范围、要求、约束、假设、风险、验证或错误成本的分支；Method 4 自行查事实。非轻量、已有持久化设计的访谈会尽早写 worklist，每个分支解决时更新；确认后生成 ADR 并修订 spec。 | 每次只问一个问题；不是独立 glossary 技能组合。文件明确注明事实/决策划分参考了 mattpocock，但未采用其 frontier 批次问法。 |
| [GitHub Spec Kit / clarify](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md) | 过滤不会实质改变实现或验证的问题，优先高影响未决事项，给出推荐选项；每接受一个答案就记录 Q/A、更新对应 spec 内容并保存。 | 先有 spec；最多五个问题且逐个提问；写回 spec 而非 glossary 与 ADR。 |
| [mik2win / FourEyes](https://github.com/mik2win/foureyes) | 作者 README 的流程图把 `/grill` 与 `/domain-model` 组合，用 `CONTEXT.md` glossary 和 ADR 保存共享语言与决策。 | 作者明确承继 Matt Pocock 与 superpowers 的方法，属于同源定制实践。具体技能文件本次未能读取，不能断言它采用本地相同的 focused 筛选或更新时机。 |
| [troioi-vn / grilling-skill](https://github.com/troioi-vn/grilling-skill) | README 要求代理先调查事实；只问前置条件已解决的决策，可独立的问题一起问并提供推荐；可逆的局部选择可能无需提问，剩余选择不能改变结果、风险、归属或完成条件时结束。 | README 没有声明 glossary/ADR 的同步落盘流程。本次直接技能文件获取失败，相关判断仅依据作者 README。 |
| [Matt Pocock / grill-with-docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) | 原文就是组合调用 `grilling` 与 `domain-modeling`，与本地参考原文一致。 | 是本地 with-docs 的来源对应，不能算另一项独立发明；入口本身没有 focused 筛选规则。 |

## 与 focused 动机直接对应的讨论

[JasonJarvan 的 issue #487](https://github.com/mattpocock/skills/issues/487) 批评原版访谈可能无限扩展，提出先阅读、只问改变交付结果的问题、按错误成本和可逆性决定追问深度，并定义停止条件。与本地 focused 的动机接近；其约五题上限是额外差异。[Matt Pocock 明确回复不同意，认为 shared understanding 已是有效停止条件](https://github.com/mattpocock/skills/issues/487#issuecomment-4924774328)。因此只能把该 issue 视为用户提出类似诉求的证据，不能视为作者认可或已采用该提案。他的简短回复针对停止条件，没有逐项讨论问题筛选或可逆性规则。

[Ic3b3rg 的 issue #906](https://github.com/mattpocock/skills/issues/906) 提议实施中发现重要未决问题时，先查 spec、文档、代码和测试；有答案则自主继续，否则问一个带推荐和取舍的 focused 问题，通过 `domain-modeling` 记录持久决策。它明确排除可逆实现细节和仓库可回答的问题。同样只确认有此公开提案。

## 判断与证据边界

公开实践已有“按后果筛选问题”和“把访谈结果写成持久文档”两种机制，也有 vvanagas 这种组合实现。本地方式的具体特点是用 focused 收缩原版设计树，保留其依赖与批次规则，再用极薄的入口接上 domain-modeling。

本次未找到名称及组合方式均与本地版本完全相同的其他公开实现。未搜到不证明不存在；公开源码与作者讨论能证明这种工作流已被表达和实现，不能据此推断使用人数或实际效果。搜索中的技能目录、转载与同源镜像未作为独立采用案例。
