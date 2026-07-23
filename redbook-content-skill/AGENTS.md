# redbook-content-skill

小红书图文内容生成技能。从主题或素材出发，生成可直接发布的竖版图文（SVG → PNG）+ 文案 + 标签。

## 激活方式

用户表达以下意图时激活：

- 「帮我写/做一篇小红书」「生成小红书图文」「做一组小红书笔记」
- 「小红书种草 / 涨粉 / 引流 / 测评 / 教程图」
- 给定素材（URL、docx、pdf、md、主题词）要求转成小红书图文

## 输入

- 主题词（如「早起习惯」「护肤种草」）
- 素材文档（URL、docx、pdf、md）
- 或两者结合

## 工作流

1. **策划确认**：锁定调性×配色×封面公式，出 ≥3 个候选方案让用户选，写入 `redbook_spec.md`
2. **内容策划**：标题钩子（≤20字）+ 每图文案 + 结尾CTA + 标签草稿
3. **封面设计**：用封面公式构图，SVG 输出，含主标题+利益点+账号名
4. **逐图生成**：SVG 1242×1660，逐图重读 spec 防漂移，字号 ramp 跨图恒定
5. **文案标签**：收敛成发布文案 + 3-8 个 #话题
6. **导出 PNG**：`python3 redbook-content-skill/scripts/svg_to_png.py <svg_dir> --out <png_dir>`
7. **QA 门禁**：对照 `references/quality-check.md`，error 必改
8. **交付**：PNG + caption.md + redbook_spec.md

## 关键纪律

- 先锁定再生成：Step 1-2 完成前不画任何像素
- 逐图重读 spec：每张图生成前 `read_file redbook_spec.md`
- 字号恒定：同角色跨图同 px，不漂移
- 只用品色：fill/stroke 仅用 spec 锁定的配色
- 安全区：顶部 ≥140px、底部 ≥180px 留空

## 参考文件

- `references/visual-system.md` — 9 种调性 × 14 套配色 × 8 种封面公式
- `references/content-anatomy.md` — 爆款图文结构与标签策略
- `references/typography.md` — 字号 ramp 与移动可读性规则
- `references/quality-check.md` — QA 门禁检查项
- `templates/redbook_spec.md` — 设计锁定文件模板

## 脚本

- `scripts/svg_to_png.py` — SVG 转 PNG（多后端回退：Playwright → resvg → cairosvg）
- `scripts/run_evals.py` — 运行评估测试

详见 `SKILL.md` 获取完整工作流和规范。
