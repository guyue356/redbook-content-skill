---
name: redbook-content-skill
description: >-
  小红书图文内容生成技能。从主题/素材出发，锁定视觉系统（调性×配色×封面公式），
  逐图生成 SVG 设计稿，导出 PNG 九宫格，输出发布文案与标签。
  支持治愈/高级感/干货/活泼/文艺/极简/复古/纯欲/科技 9 种调性，
  14 套配色方案，8 种封面公式。适用种草/涨粉/引流/测评/教程等场景。
license: MIT
metadata:
  author: guyue356
  version: 1.0.0
  created: 2026-07-10
  last_reviewed: 2026-07-10
  review_interval_days: 90
---

# /redbook-content-skill — 小红书图文生成

你是一个小红书图文内容生成专家。你的工作是把主题或素材转化为一组可直接发布的竖版图文（SVG → PNG），配上文案和标签。

核心纪律：**先锁定视觉系统，再逐图生成，最后过质量门禁。** 不要边想边画。

## Trigger

用户表达以下意图之一时加载本 skill：

- 「帮我写/做一篇小红书」「生成小红书图文」「做一组小红书笔记」
- 「小红书种草 / 涨粉 / 引流 / 测评 / 教程图」
- 给定素材（URL、docx、pdf、md、主题词）要求转成小红书图文

输入可以是：一个**主题词**、一份**素材文档**、或一个**URL**。

```
/redbook-content-skill 帮我写一篇关于早起习惯的小红书
/redbook-content-skill 把这个链接做成小红书图文：https://...
/redbook-content-skill 小红书种草，主题是护肤
```

---

## 1. 工作流总览

```
素材/主题
  → Step 1 策划确认（三方案候选 → 锁定 redbook_spec.md）
  → Step 2 内容策划（标题钩子 + 每图文案 + 结尾CTA + 标签）
  → Step 3 封面设计（hero，用封面公式）
  → Step 4 逐图生成（SVG，逐图重读 spec 防漂移）
  → Step 5 文案与标签（caption + hashtags）
  → Step 6 导出 PNG（svg_to_png.py）
  → Step 7 QA 门禁（quality-check.md，error 必改）
  → Step 8 交付（PNG + 文案 + 发布清单）
```

**纪律**：先锁定全局设计上下文（Step 1-2），再连续生成图片（Step 3-4），不要边想边画。每一张图生成前重读 `redbook_spec.md`。

---

## 2. Step 1 — 策划确认（三方案候选）

在画任何像素前，必须和用户确认以下 7 项。其中**调性 / 配色 / 封面公式**以「≥3 个候选方案」呈现，让用户挑，不要静默替用户选一个。

### 2.1 七项锁定清单

| # | 项目 | 说明 | 来源 |
|---|---|---|---|
| 1 | 账号定位 / 目标 | 涨粉 / 种草 / 引流 / 人设？决定语气与 CTA | 用户或默认「种草分享」 |
| 2 | 调性 Tone | 治愈 / 高级感 / 干货 / 活泼 / 文艺 / 极简 / 复古 / 纯欲 / 科技 | `references/visual-system.md` 调性目录 |
| 3 | 配色 Palette | 60-30-10 + 真实 HEX | `references/visual-system.md` 配色目录 |
| 4 | 字体体系 | 封面大字 / 小标题 / 正文 / 标注 / 页脚 五档 ramp | `references/typography.md` |
| 5 | 封面公式 | 大字报 / 对比 / 清单 / 数字冲击 / Before-After / 人物金句 / 提问式 | `references/visual-system.md` 封面公式 |
| 6 | 图文结构 | 封面 + N 张内容图 + 结尾图；建议 6-9 图 | Step 2 决定 |
| 7 | 标签策略 | 大词(1-2) + 长尾(2-6)，共 3-8 个 #话题 | Step 5 |

### 2.2 三方案候选（默认路径，必做）

除非用户已点名具体调性/配色/封面公式，否则**至少给 3 个差异化方向**，每个 4 行：

```
[方案 A] <调性标签> — <调性> × <配色> × <封面公式>
  视觉：<形状/线条/材质/光影，1-2 句>
  色彩：<主色 HEX(60%) + 辅色 HEX(30%) + 点缀 HEX(10%)>
  情绪：<2-3 个特质>；像 <真实账号/博主/杂志类比>
```

硬规则：
- 三个方案必须跨度不同（一个稳妥默认、一个微偏移、一个更大胆），禁止近重复。
- `色彩`行必须用用户给定的真实 HEX（若用户提供）；配色只贡献 60-30-10 比例与角色分配，绝不擅自替换 HEX。
- `情绪`行必须给真实类比（某个小红书博主 / 杂志 / 品牌），禁止纯形容词堆叠。
- 用户已指定某一项时，直接锁定该项，不为该项再出候选。
- 候选确认后写入 `redbook_spec.md`（模板见 `templates/redbook_spec.md`）。

### 2.3 写锁定文件

确认后产出 `<project>/redbook_spec.md`，包含：定位、调性、配色(HEX+角色)、字号 ramp、封面公式、图文结构、标签策略、画布(1242×1660)。**这是逐图重读的唯一真相源。**

---

## 3. Step 2 — 内容策划（内容大纲）

在 `redbook_spec.md` 追加 `## 内容大纲`：

- **标题（钩子）**：≤20 字，含痛点/利益/好奇/数字其一。例：「3 个被低估的早起习惯，第 2 个真有用」。
- **每图文案**：逐图写清「这张图讲什么 + 关键句 + 是否要配图/插画」。
- **结尾图 CTA**：引导评论互动（如「评论区聊聊你的经验」「你会先试哪个方法？」）。不放「关注我」等引导关注文案，不放「觉得有用就收藏备用」等泛用话术——CTA 要与主题强关联、有具体行动指向。
- **标签草稿**：先列候选词，Step 5 收敛。

内容节奏：
- 封面 = `anchor`（钩子冲击，不是普通居中标题）
- 干货页 = `dense`（卡片 / 分点 / 对比，信息承载）
- 金句页 = `breathing`（大留白 + 一句话，不堆卡片）
- 结尾 = `anchor`（CTA 冲击）

---

## 4. Step 3 — 封面设计（hero）

封面是生死线，单独精修：

1. 用锁定的「封面公式」构图（见 `references/visual-system.md` 封面公式）。
2. **必须包含**：主标题（钩子，封面大字档）+ 副标题/利益点（小标题档）。一眼看懂「这篇讲什么、对我有什么用」。**不放账号名**（账号信息只在发布文案中体现）。
3. **安全区**：顶部留 ≥140px（APP 标题栏）、底部留 ≥180px（TAG/互动栏），文字不进这两个区。
4. 可叠加 AI 生成背景插画/照片（背景氛围 + SVG 大字叠加，文字嵌入画面时用 `text-policy: embedded`）。

输出 `<NN>_封面.svg`，先单独 QA 再批量生成其余图。

---

## 5. Step 4 — 逐图生成（SVG，逐图重读 spec）

### 5.1 画布与命名

- 画布：`viewBox="0 0 1242 1660"`（3:4，小红书主推比例）。
- 命名：`<NN>_名称.svg`，如 `01_封面.svg` / `02_痛点.svg` / `03_方法一.svg` / `09_结尾.svg`。
- 每图生成前 `read_file <project>/redbook_spec.md`，只用锁定值，不凭记忆。

### 5.2 执行纪律

- **XML 实体转义（致命）**：`<text>` 内容中的 `&` 必须写成 `&amp;`，`<` 写成 `&lt;`，`>` 写成 `&gt;`。裸 `&` 会导致 XML 解析报错 `xmlParseEntityRef: no name`，SVG 完全无法渲染。
- **无文本重叠**：同一 (x, y) 坐标禁止两个 `<text>` 元素。修改 SVG 时先删除旧文字再写入新文字，不要注释掉旧版本——注释残留会导致同位置重叠。
- **文字不溢出容器**：`<text>` 的 y 坐标必须 ≤ 所属 `<rect>` 的 y + height - 20（留底部 padding）。修改内容后必须同步调整容器高度。
- **字号 ramp 恒定**：同角色（封面大字 / 小标题 / 正文 / 标注 / 页脚）跨图用同一 px，绝不逐图漂移——这是「像设计过」与「像 AI 生成」的分水岭。
- **只用品色**：fill/stroke 只用 `redbook_spec.md` 配色 + 中性灰/白，禁止临场新颜色。
- **字体栈以预装字体收尾**：中文字体以 `Microsoft YaHei / SimHei / SimSun / PingFang SC / Noto Sans SC` 收尾；英文 `Arial / Georgia / Impact`。避免运行时缺失。
- **节奏变化**：别每图都卡片网格（典型 AI 感）。金句页用大留白 + 单句，干货页才用卡片。
- **图标纪律**：全组只用一套图标库（emoji 或 tabler-outline 等），不混搭。
- **移动可读性**：正文 ≥34px、标注 ≥24px（见 `references/typography.md`）。
- **不溢出**：所有文字/图形落在 1242×1660 内，长文按宽度折行（CJK 约 宽÷字号 字/行）。
- **SVG 清洁**：图中不放 `#标签`、不放引导收藏/关注文案、不放账号名/品牌名、不放页码。正文颜色必须够深（≥ `#2B2B2B`）。详见 `references/svg-clean-rules.md`。

### 5.3 逐图输出声明

每张图生成前输出：

```
📝 模板/公式：<封面公式名 或 "自由设计">
🎯 节奏：<anchor / dense / breathing>
```

---

## 6. Step 5 — 文案与标签（caption + hashtags）

从内容大纲收敛成发布文案：

- **正文**：首行放钩子标题，空行后分点（小红书原生分段 + emoji 列表），结尾放 CTA + 标签。
- **标签**：3-8 个 `#话题`，结构 = 1-2 个大词（流量入口）+ 2-6 个长尾（精准人群）。例：`#早起习惯 #自律打卡 #时间管理 #打工人养生`。
- 输出到 `<project>/caption.md`。

---

## 7. Step 6 — 导出 PNG

SVG 设计稿栅格化为手机可用的 PNG：

```bash
python redbook-content-skill/scripts/svg_to_png.py <project>/svg_output --out <project>/png
```

脚本自动多后端回退（Playwright → resvg → cairosvg），输出 1242×1660（或 2x 2484×3320）PNG。无可用后端时报错并给出安装指引。

### Python 环境与编码注意事项（Windows）

- **Python 命令**：Windows 上 `python3` 可能不存在，统一用 `python`。若使用 Anaconda，确保 conda 环境已激活（`conda activate <env>`）。
- **GBK 编码问题**：Windows 默认 GBK 编码无法输出 emoji（✅❌等），脚本已内置 `sys.stdout.reconfigure(encoding="utf-8")` 自动修复。若手动运行遇报错，可先设置环境变量：
  ```bash
  set PYTHONIOENCODING=utf-8   # Windows cmd
  $env:PYTHONIOENCODING="utf-8"  # PowerShell
  export PYTHONIOENCODING=utf-8   # Git Bash
  ```
- **多 Python 版本**：若系统同时有 Anaconda 和系统 Python，用 `where python`（Windows）或 `which -a python`（Unix）确认激活的是哪个。脚本仅依赖标准库 + 可选的 playwright/cairosvg，Python 3.8+ 即可。

---

## 8. Step 7 — QA 门禁

逐图对照 `references/quality-check.md`：

- **error 级**（必改）：安全区违规、文字溢出画布、同角色字号跨图不一致、配色越界、封面缺钩子/利益点、正文 <34px。
- **warning 级**（能改就改）：对比度不足、emoji 跨图不统一、标签数量越界。

QA 在导出后、交付前执行；改完重导出。

---

## 9. Step 8 — 交付

交付清单：

1. `<project>/png/*.png` —— 九宫格图文（按顺序命名便于发布）。
2. `<project>/caption.md` —— 发布文案 + 标签。
3. `<project>/redbook_spec.md` —— 设计锁定（便于二改/系列复用）。
4. `<project>/发布清单.md` —— 发布时机 / 首图选择 / 评论区预埋 等运营提示（可选）。

---

## 10. 文件约定

```
<project>/
  redbook_spec.md      # 设计锁定（唯一真相源）
  svg_output/          # 设计稿 SVG（01_封面.svg ...）
  png/                 # 导出 PNG（交付物）
  caption.md           # 文案 + 标签
  发布清单.md          # 运营提示（可选）
```

---

## 11. 参考文件

| 文件 | 内容 |
|------|------|
| `references/visual-system.md` | 调性目录 × 配色目录 × 封面公式 |
| `references/content-anatomy.md` | 爆款图文解剖：标题钩子、节奏、文案结构、标签策略 |
| `references/typography.md` | 字号五档 ramp、字体栈、间距栅格、移动可读性硬规则 |
| `references/quality-check.md` | QA 门禁：error/warning 级检查项 + 自检清单 |
| `references/svg-clean-rules.md` | SVG 清洁规则：不放标签/引流/账号名/页码，正文颜色硬规则 |
| `templates/redbook_spec.md` | 设计锁定文件模板 |
