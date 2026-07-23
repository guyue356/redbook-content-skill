# redbook-content-skill 评估规范

## 二元检查

| # | 检查项 | 判定方式 | 通过条件 |
|---|--------|----------|----------|
| 1 | SKILL.md frontmatter | shell: `head -1 SKILL.md` | 首行为 `---` |
| 2 | SKILL.md 标题格式 | shell: `grep "^# /" SKILL.md` | 匹配 `# /redbook-content-skill` |
| 3 | SKILL.md 行数 | shell: `wc -l SKILL.md` | ≤500 行 |
| 4 | 参考文件完整 | shell: `ls references/*.md` | 4 个文件全部存在 |
| 5 | 模板文件存在 | shell: `ls templates/redbook_spec.md` | 文件存在 |
| 6 | 脚本语法正确 | shell: `python3 -c "import py_compile; py_compile.compile('scripts/svg_to_png.py', doraise=True)"` | 无报错 |
| 7 | 调性目录完整 | llm-judge: visual-system.md 包含全部 9 种调性 | 9/9 命中 |
| 8 | 配色目录完整 | llm-judge: visual-system.md 包含 ≥10 套配色方案 | ≥10 套 |

## 金用例

### Case 1: 主题词输入

- **输入**: `帮我写一篇关于早起习惯的小红书`
- **期望**: 产出 redbook_spec.md（含调性×配色×封面公式锁定）+ ≥3 个候选方案 + caption.md + ≥3 张 SVG
- **验证**: 文件存在 + spec 包含七项锁定 + caption 包含 3-8 个标签

### Case 2: 素材文档输入

- **输入**: 一份护肤成分科普文档 + `做成小红书种草`
- **期望**: 从文档提取关键信息，生成护肤主题图文，调性偏向治愈/纯欲
- **验证**: 内容与输入素材相关 + 标签含护肤相关大词

### Case 3: URL 输入

- **输入**: 一个文章 URL + `转成小红书图文`
- **期望**: 提取文章核心观点，生成信息图式图文
- **验证**: 内容与原文一致 + 封面含钩子 + 图文结构合理
