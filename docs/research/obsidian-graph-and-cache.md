# 本机 Obsidian 的关系图与缓存

研究时间：2026-10-01。对象：本机安装的 Obsidian 1.13.7。结论来自原版应用 bundle、当前 vault 的配置与磁盘记录，以及官方文档。

**Graph View 从 metadata 的引用关系生成图，布局在独立 worker 中计算。它有持久化的 metadata 缓存和图设置，也会在打开的视图中保留节点与坐标；本次没有发现桌面 Graph View 把完整 nodes/edges 或布局坐标保存成持久化图缓存。**这里的“没有发现”限定于追踪的核心实现和检查的文件，不能扩展成所有插件或所有浏览器存储都不存在这类数据。

## 前次研究与本次范围

开始前已阅读 vault 根 `AGENTS.md` 和 [前次 Markdown 处理研究](</Users/situ/Library/Mobile Documents/iCloud~md~obsidian/Documents/situ-vault/002 AI Workspace/Obsidian markdown 处理逻辑.md>)。前次确认 metadata worker 从 Markdown AST 提取 links、embeds、frontmatterLinks 和 tags，文件 resolver 再把链接文字解析成 vault 文件。本次继续追踪这些数据如何进入 Graph View，区别桌面图、Publish 图、磁盘缓存与视图内存。[来源：前次笔记；源码 A 的 `uD`、`CD`、`MetadataCache.resolveLinks`]

本次没有修改 vault 笔记、Graph View 设置或应用缓存。没有为了检查缓存而启动、关闭、重置应用。

## 构图路径

```text
Markdown / 支持文件的引用提取器
  → metadataCache 中的文件元数据
  → resolveLinks：resolvedLinks + unresolvedLinks
  → h0.render：全局 nodes 与 links
  → m$：可选的局部图裁剪
  → 孤立节点过滤与当前文件高亮
  → v$.setData：更新视图中的节点和边
  → sim.js：力学布局
  → PIXI：画节点、文字、线与箭头
```

`a0` 是全局图视图，`l0` 是局部图视图；两者使用 `h0` 数据引擎与 `v$` renderer，并监听 metadataCache 的 `resolved` 事件触发更新。`h0.load` 还监听文件创建、修改、重命名和单文件 `resolve`，供搜索结果重新计算。[来源：源码 A，`a0.onload`、`l0.load`、`h0.load`、`h0.render`]

### 文件边从哪里来

`resolveLinks(path)` 调用 `iterateRefsForFile`。普通 Markdown 的引用由 `CD` 遍历 **frontmatterLinks、links、embeds**；注册了专用 link updater 的文件扩展名则交给对应提取器。每个引用经过 `bD` 去除第一个 `#` 及后续内容，再调用 `getFirstLinkpathDest`。已解析目标记入 `resolvedLinks[source][targetPath]`，未解析目标记入 `unresolvedLinks[source][normalizedLinktext]`，值为引用次数。[来源：源码 A，`MetadataCache.resolveLinks`、`iterateRefsForFile`、`CD`、`bD`]

因此，桌面图中的关系不只来自正文 WikiLink：正文内部 Markdown 链接、嵌入、被 metadata 提取的 frontmatter 内部链接都能参与。标题与块引用归到所属文件，不创建单独的标题或块节点；外部 URL 不属于这些内部引用。前次原版 worker 样例还确认 `%%[[hidden]]%%` 会进入 metadata，所以不能把图概括为“只扫描可见正文”。frontmatter 的任意普通字符串不会自动变成边，仍须由原解析器识别成内部引用。[来源：前次笔记的“Frontmatter 和 metadata”；源码 A，`CD`、`bD`、`cD`]

`h0.render` 的构图函数遍历 `getCachedFiles()`，以文件完整路径作为节点 ID；从 resolved/unresolved maps 复制目标到节点的 `links` 对象，值变为 `true`。同一源文件多次引用同一目标仍是一条有向边，metadata 中的引用次数不作为这条图边的权重。箭头显示只是可选绘制设置，底层边仍保存源与目标。[来源：源码 A，`h0.render` 内联 `function(e,t,n,i)`、`d$`、`v$.setData`；[官方 Graph View](https://help.obsidian.md/plugins/graph)]

### 节点、标签与过滤

| 项目 | 本机实现 |
| --- | --- |
| 文件节点 | 默认不把 `md`、`canvas`、`base` 当附件；其余扩展名由 `Cb` 归到 attachment 类别，受附件开关控制 |
| 未创建文件 | `hideUnresolved=false` 时，从 surviving source 的 unresolved map 建立 unresolved 节点；打开 Existing files only 则跳过它们 |
| 标签 | `showTags=true` 时，`MD` 合并 frontmatter tags 和正文 tags，建立文件 → 标签边与 tag 节点；通过全库 `getTags()` 的小写索引统一大小写变体的显示形式 |
| 搜索 | 使用应用搜索引擎 `AP` / `PP` 计算文件筛选结果；标签调用 `matchTag`，附件调用 `matchFilepath`；不是简单文件名包含判断 |
| 分组颜色 | 匹配的 color query 给节点着色；多个颜色分组按搜索数组顺序处理，首个匹配颜色生效 |
| 排除文件 | 构图源节点检查 `isUserIgnored(path)`，对应官方 Excluded files |
| 孤立节点 | 关闭 showOrphans 后，删除没有其他 surviving 节点入边、也没有指向其他 surviving 节点出边的节点；仅自引用不算连接 |

来源：源码 A，`Cb` / `bb`、`MD` / `ZT`、`MetadataCache.getTags`、`h0.setQuery`、`h0.render`；[官方 Graph View](https://help.obsidian.md/plugins/graph)。`md/canvas/base` 的分类只说明节点筛选规则；本次没有逐项追踪 Canvas 与 Bases 的专用引用提取算法。标签关系基于解析出的标签字段，不是文本主题相似度。

全局节点大小默认取 renderer 中 unique forward 与 reverse 邻接数量，再由 `getSize` 使用平方根映射到绘制半径；不会按正文重复引用次数增大。双向各有一条边时 forward 和 reverse 分别计入；局部图使用下面的 depth 权重覆盖这一默认大小。[来源：源码 A，`p$.getRelated`、`p$.getSize`、`v$.setData`]

### 局部图的规则

`m$(graph, options)` 从 `localFile` 开始，按 `localJumps` 分层扩展。`localForelinks` 控制向外引用，`localBacklinks` 控制向内引用；`localInterlinks` 打开后恢复选中节点之间的原始边，关闭时保留扩展过程中连接新节点的边。每层新节点的 weight 为 `30 - 30 / localJumps * (层序号 + 1)`，中心节点为 30。[来源：源码 A，`m$`；[官方局部图说明](https://help.obsidian.md/plugins/graph)]

**标签可以出现在局部图，但扩展在 tag 节点处停止。**两个笔记共享一个标签，不能仅靠提高深度就让第二个笔记通过这个标签进入核心局部图：`m$` 跳过 tag 类型源节点，并用 `c$={tag:true}` 阻止从 tag 节点继续扩展。中心文件不在构图结果时，函数返回单独中心节点。[来源：源码 A，`m$`、`c$`]

## 布局与视图内存

`v$.setData` 比较新旧图：保留相同 ID 的 `p$` 节点对象，增删有向 `d$` 边，只给新增节点生成初始随机坐标。已有节点在发给 worker 的 `nodes` map 中用 `false` 表示，新增节点用 `[x,y]`；worker 因而保留已有节点的位置与速度。这是打开视图内的增量复用，不是每次刷新都从零随机排布。[来源：源码 A，`v$.setData`；源码 S，`self.onmessage`]

专用 `Graph Worker` 加载 `/sim.js`。该 worker 优先实例化内嵌 WebAssembly 布局实现，无法使用时才走 bundle 内的 JavaScript 力学模拟。JS 路径包含 x/y 中心拉力、link、many-body 排斥与 collision 力；源码不能简化为“PIXI 算布局”或“始终用 D3 算布局”。节点坐标以 Float32 buffer 回传；支持时使用 SharedArrayBuffer，否则使用可转移 ArrayBuffer。[来源：源码 A，`v$` 构造器、`renderCallback`；源码 S，WebAssembly 初始化、`Using fallback d3 simulator` 分支、`Y`]

Renderer 保存 `nodes`、`nodeLookup`、`links` 与最新 workerResults；worker 保存 `F` 节点表、`M` 节点列表、`G` 边列表和模拟状态。拖动通过 `forceNode` 固定坐标；`destroy()` 终止 worker 并销毁绘制对象。本次追踪的 Graph View 保存入口没有把这些对象序列化到磁盘。[来源：源码 A，`v$.destroy`、`v$.setData`；源码 S，`self.onmessage`]

## 磁盘上确实保存了什么

| 数据 | 持久化位置或内存位置 | 本次结论 |
| --- | --- | --- |
| 文件 metadata | IndexedDB `<appId>-cache` 的 `file`、`metadata` stores | 有持久化缓存；它是构图输入 |
| 已解析 / 未解析邻接表 | `metadataCache.resolvedLinks` / `unresolvedLinks` | 内存索引；初始化会从缓存引用重新 resolve |
| 全局图设置 | vault `.obsidian/graph.json` | 有设置；检查文件未见 nodes/edges/positions |
| 局部图文件与设置 | vault `.obsidian/workspace.json` 的 localgraph state | 有工作区状态与 options；检查条目未见坐标 |
| 当前图拓扑与坐标 | renderer 和 sim worker | 打开的视图中增量保留；未发现核心桌面持久化入口 |

官方说明 IndexedDB 在应用关闭后保留 metadata cache，供 Graph View、Outline 等功能使用；macOS 全局目录是 `~/Library/Application Support/obsidian`，workspace JSON 保存工作区布局。[来源：[官方 How Obsidian stores data](https://raw.githubusercontent.com/obsidianmd/obsidian-help/master/en/Files%20and%20folders/How%20Obsidian%20stores%20data.md)]

本机 `situ-vault` 对应 `appId=6f88ce6ccb455d1e`，由全局 `obsidian.json` 的 vault 路径映射确认。实际物理目录是：

```text
/Users/situ/Library/Application Support/obsidian/IndexedDB/
  app_obsidian.md_0.indexeddb.leveldb/
```

该目录约有 30 MB 文件；`024668.log` 与 `024672.ldb` 中发现 UTF-16 数据库名 `6f88ce6ccb455d1e-cache`。这是磁盘签名证据，不是对 LevelDB 全部逻辑记录的解码；因此不能由该体积推算“图缓存大小”，也没有读取出当前全部笔记/边数量。[来源：磁盘 D1、D2]

`MetadataCache._preload` 以 `Xk(this.app.appId + "-cache", 19, …)` 打开 IndexedDB，创建 `file` 和 `metadata` 两个 stores；前者用 path 保存 `{mtime,size,hash}`，后者用内容 hash 保存序列化后的 parsed metadata。`saveMetaCache` 处理位置压缩后保存。初始化对 mtime、size 和 hash 对应 metadata 做复用检查；即使命中缓存，也会 `queueFileForLinkResolution`，重建 resolved/unresolved maps。也就是说，缓存避免重复解析全文，但不代表直接从磁盘加载已经裁剪、着色、排好坐标的 Graph View。[来源：源码 A，`MetadataCache._preload`、`initialize`、`saveFileCache`、`saveMetaCache`、`resolveLinks`]

全局插件 `r0.saveOptions` 调用 plugin.saveData；`h0.getOptions` 收集过滤、分组、显示、forces，另外保存 scale 和 controls close。本机 graph.json 确有这些字段。局部图 `l0.getState` 保存文件视图 state 与 engine options，并用 requestSaveLayout 持久化；本机 workspace.json 的 localgraph 指向前次研究笔记，深度为 1，前向/后向链接打开，邻居互连关闭。它们是用户设置与工作区状态，不能当成图拓扑快照。[来源：源码 A，`r0.saveOptions`、`h0.getOptions`、`l0.getState` / `onOptionsChange`；磁盘 D3、D4]

## 不要混淆 Publish 的缓存

同一 app.js 还打包了 Publish 图 `y$`。它的 `getGraphData` 使用 `_graphData` 缓存 Promise，调用 `b$` 从站点 cache 构图；这是 Publish 运行时的内存缓存，**不是桌面 `h0.render` 的实现**。`b$` 遍历 `kD`（links、embeds），桌面引用索引则通过 `CD` 包括 frontmatterLinks；两条路径不能互相代替来推断行为。[来源：源码 A，`y$.getGraphData`、`b$`、`kD`、`CD`]

## 证据与复查边界

源码 A：安装包 `/Applications/Obsidian.app/Contents/Resources/obsidian.asar` 中的 `app.js`。压缩函数名与字符 offset 只对这份 hash 有效。

```text
Obsidian: 1.13.7
asar SHA-256:   a52a7daf1e2460bae03de80f2816604bd16a56cd374fbe5ce8d1a9ef5604059d
app.js SHA-256: 8efbf581e259cabef4f9c9a34814cfe3c02863757377e56b3603933c50e89898
sim.js SHA-256: 549be2f69710af360d521c92b80c83718f673594d3dc2255a65e251199eee25d
```

源码 S 是同一 asar 中的 `sim.js`（17,693 bytes）。只读解包产物在 `/tmp/obsidian-markdown-research/`；临时目录可清理，版本、hash 与符号可用于重新定位原应用。关键入口：`CD` 字符 offset 1,373,673 附近，`MetadataCache.resolveLinks` 1,748,292 附近，`m$` 2,360,243，`h0.render` 内联 builder 2,683,260，`h0.getOptions` 2,688,141 附近。符号优先于近似 offset。

磁盘 D1：`/Users/situ/Library/Application Support/obsidian/obsidian.json`；D2：上文 IndexedDB LevelDB 目录；D3/D4：`situ-vault/.obsidian/graph.json` 和 `situ-vault/.obsidian/workspace.json`。只读取与本次目标有关的配置与数据库名称签名，没有复制私人笔记内容到仓库。

独立行为检查直接在 Node vm 执行原版 sim.js，只注入 `self`、结果收集与可控的 setTimeout 队列：两个节点及一条边产生有限 Float32 坐标；forceNode 把 A 固定到 `[10,20]`；下一条消息删除 B 后回传仅剩 A。WebAssembly 路径成功，未打印 fallback 日志。脚本与输出在 `/tmp/obsidian-graph-research/check-sim.cjs` 和 `sim-results.json`。这覆盖 worker 消息与坐标状态，不覆盖 live DOM/PIXI、真实调度、SharedArrayBuffer、布局收敛或跨应用重启持久化。

另一组检查抽取原版 `h0.render` 内联 builder 与 `m$`，以人工 metadata fixture 执行：A 对 B 引用 3 次，在图中仍是 `B:true` 一条边；附件隐藏时不产生图片边；重复 unresolved target 仍为一条边；`#topic` 根据全库 tag map 合并到 `#Topic`；同时关闭 unresolved 和 tags 后只剩 B 边；`A → #t ← B` 在局部深度 2、双向遍历下没有借标签拉入 B。脚本与结果为 `/tmp/obsidian-graph-research/check-builder.cjs`、`builder-results.json`。它给 `Cb`、`MD`、`isBoolean` 提供针对 fixture 的输入适配，未验证完整 metadata 解析、搜索、timelapse 或前端，因此属于聚焦的源码行为刻画。

前次原版 metadata worker 行为记录为输入语义提供补充；本次主要结论来自源码追踪与只读磁盘核查。未完整解码当前 IndexedDB stores，未实测关闭/重开后的图坐标，也未审查全部第三方插件。持久化坐标的结论以“核心实现未发现保存入口”表述，避免把未运行的场景写成已验证事实。

## 与 situ-note 包的全库比较

随后检查了 `/Users/situ/Codes/situ-note/packages/astro-obsidian-content-provider/`。用户提到的 `situ-notes` 对应本机实际存在的单数目录。比较时间仍为 2026-10-01；包目录包含尚未提交的修改，结论针对本机当时的源码。检查的八个相关模块，其 TypeScript 转译结果与执行的 dist JavaScript 完全一致。

vault 的 `.obsidian/graph.json` 是设置文件，无法直接和节点/边导出比较。本次生成两个使用同一格式的邻接表 JSON：全库 Markdown 笔记作为节点、直接解析到 Markdown 笔记的引用作为去重有向边。这样排除了标签、附件、未解析节点、Canvas/Bases 和 Graph View 的用户筛选；它比较的是笔记引用关系，不是完整可视化图。

官方基线由原版 `worker.js` 解析完整笔记，再用原版 `getLinkpathDest` / `getFirstLinkpathDest` 处理 frontmatterLinks、links、embeds；文件名索引由同一份完整 vault 文件列表提供。包侧执行真实 `readVault`、`createResolver` 和 `createNoteGraph`，没有应用发布筛选。它是从安装源码重建的官方等价基线，不是运行中应用的 Graph View 导出；没有覆盖第三方引用提取器或实际缓存状态。[来源：`/tmp/obsidian-graph-research/compare-package.mjs`；源码 A；包 `src/core/graph.ts`、`vault.ts`、`resolve.ts`]

| 项目 | 结果 |
| --- | ---: |
| Markdown 节点 | 3,353 |
| 官方基线的唯一有向边 | 3,917 |
| 包的唯一有向边 | 3,910 |
| 两者共有的边 | 3,908 |
| 包缺少的官方边 | 9 |
| 包额外生成的边 | 2 |
| 对官方解析出的引用，两个 resolver 目标不同的次数 | 0 |

最后一项只保证本次共享文件索引和实际引用输入上的一致，不能当作所有路径输入的 resolver 等价证明。

### 11 条差异的原因

| 原因 | 当前 vault 中的边差异 | 聚焦复现 |
| --- | ---: | --- |
| 数学块结束规则不同 | 缺少 5 | `$$x\n=y$$\n\n[[Target]]`：原版得到 Target 引用；包的 remark-math 将后面的链接纳入 math 节点。把关闭 `$$` 放到独立行，包重新得到引用 |
| tab 缩进列表中的代码围栏边界不同 | 缺少 2 | `- A\n\t```java\n\t  ```\n\t- B\n\t\t- [[Target]]`：原版得到 Target；包仍把后文当代码。对齐关闭围栏后包得到引用 |
| WikiLink 显示文字内含方括号 | 缺少 1 | `[[Target\|双 [ ]]]`：原版得到 Target；包的 tokenizer 遇到 `[` 即拒绝。去掉显示文字中的方括号后包得到引用 |
| frontmatter 链接没有进入包的图 | 缺少 1 | `related: "[[Target]]"`：原版 frontmatterLinks 收录；包读取后只对 body 建图，没有遍历 properties |
| 空 Markdown URL 被当作当前笔记 | 额外 2 | `[label]()`：原版 metadata 不产生引用；包接受空 URL，resolver 把空 path 返回为 source，得到自环 |

表中的 `\n`、`\t` 表示实际换行和 tab；WikiLink 示例中的反斜线仅用于转义表格竖线。普通 `[[Target]]`、不带方括号的显示文字、独立行关闭数学块、对齐的 tab 代码围栏都作为控制样例通过。源代码入口分别是 `src/core/transform/parser.ts`、`remark-obsidian-links.ts`、`graph.ts`、`links.ts` 和 `resolve.ts`。

此外，`%%[[Target]]%%` 的独立样例确认另一项语义差异：官方 metadata 保留该引用，包先调用 `hideComments` 将其移除。本次真实 vault 没有因此产生额外的唯一边差异；这不代表两者对注释的行为相同。[来源：`check-differences.mjs` 与 `comparison/minimal-cases.json`]

结果表明该包目前是为发布选择提供的引用图，尚不等价于桌面 Obsidian 的 metadata 引用图。frontmatter 和注释差异属于当前图的数据来源选择；数学、代码围栏、带方括号别名和空 URL 则是具体的解析/建边差异。

可复查产物都在 `/tmp/obsidian-graph-research/`：

- `comparison/official.graph.json`、`comparison/package.graph.json`：两个完整的规范化邻接表。
- `comparison/difference.json`：11 条差异及官方引用位置/来源类别；没有保存笔记全文。
- `comparison/minimal-cases.json`、`minimized-vault-cases.json`：人工控制样例与两个从真实笔记按行缩减的代码围栏复现。
- `compare-package.mjs`：全库比较命令为 `node /tmp/obsidian-graph-research/compare-package.mjs`；发现差异时断言失败，JSON 在断言前已经保存。
- `check-differences.mjs`：上述聚焦差异与控制样例的断言全部通过。
