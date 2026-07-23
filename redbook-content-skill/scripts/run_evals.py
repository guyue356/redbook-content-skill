#!/usr/bin/env python3
"""
redbook-content-skill 评估运行器

运行二元检查 + 金用例验证，确认技能结构和功能完整。

用法：
    python3 run_evals.py <skill_dir>           # 运行所有检查
    python3 run_evals.py <skill_dir> --validate # 仅验证结构
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple


def check_file_exists(path: Path, label: str) -> bool:
    """检查文件是否存在。"""
    if path.exists():
        print(f"  [OK] {label}: {path.name}")
        return True
    else:
        print(f"  [FAIL] {label}: {path.name} 缺失")
        return False


def check_frontmatter(skill_md: Path) -> bool:
    """检查 SKILL.md 是否有 YAML frontmatter。"""
    content = skill_md.read_text(encoding="utf-8")
    if content.startswith("---"):
        print("  [OK] SKILL.md 包含 YAML frontmatter")
        return True
    else:
        print("  [FAIL] SKILL.md 缺少 YAML frontmatter")
        return False


def check_skill_name(skill_md: Path) -> bool:
    """检查 SKILL.md 标题是否以 # / 开头。"""
    content = skill_md.read_text(encoding="utf-8")
    for line in content.split("\n"):
        if line.startswith("# "):
            if line.startswith("# /"):
                print(f"  [OK] 标题格式正确: {line.strip()}")
                return True
            else:
                print(f"  [FAIL] 标题应以 '# /' 开头，实际: {line.strip()}")
                return False
    print("  [FAIL] 未找到标题行")
    return False


def check_line_count(skill_md: Path, max_lines: int = 500) -> bool:
    """检查 SKILL.md 行数是否在限制内。"""
    lines = len(skill_md.read_text(encoding="utf-8").split("\n"))
    if lines <= max_lines:
        print(f"  [OK] SKILL.md 行数: {lines}/{max_lines}")
        return True
    else:
        print(f"  [FAIL] SKILL.md 行数超限: {lines}/{max_lines}")
        return False


def check_references(skill_dir: Path) -> bool:
    """检查参考文件是否完整。"""
    refs_dir = skill_dir / "references"
    expected = [
        "visual-system.md",
        "content-anatomy.md",
        "typography.md",
        "quality-check.md",
    ]
    all_ok = True
    for name in expected:
        path = refs_dir / name
        if not check_file_exists(path, f"参考文件"):
            all_ok = False
    return all_ok


def check_templates(skill_dir: Path) -> bool:
    """检查模板文件是否完整。"""
    tpl_dir = skill_dir / "templates"
    return check_file_exists(tpl_dir / "redbook_spec.md", "模板文件")


def check_scripts(skill_dir: Path) -> bool:
    """检查脚本文件是否完整。"""
    scripts_dir = skill_dir / "scripts"
    return check_file_exists(scripts_dir / "svg_to_png.py", "转换脚本")


def check_svg_to_png_syntax() -> bool:
    """检查 svg_to_png.py 语法是否正确。"""
    try:
        import py_compile
        script = Path(__file__).parent / "svg_to_png.py"
        if not script.exists():
            print("  [FAIL] svg_to_png.py 不存在，跳过语法检查")
            return False
        py_compile.compile(str(script), doraise=True)
        print("  [OK] svg_to_png.py 语法正确")
        return True
    except py_compile.PyCompileError as e:
        print(f"  [FAIL] svg_to_png.py 语法错误: {e}")
        return False


def run_structure_checks(skill_dir: Path) -> Tuple[int, int]:
    """运行结构检查，返回 (通过数, 总数)。"""
    print("=" * 50)
    print("结构检查")
    print("=" * 50)

    checks = [
        ("SKILL.md 存在", lambda: check_file_exists(skill_dir / "SKILL.md", "主文件")),
        ("AGENTS.md 存在", lambda: check_file_exists(skill_dir / "AGENTS.md", "伴随文件")),
        ("frontmatter", lambda: check_frontmatter(skill_dir / "SKILL.md")),
        ("标题格式", lambda: check_skill_name(skill_dir / "SKILL.md")),
        ("行数限制", lambda: check_line_count(skill_dir / "SKILL.md")),
        ("参考文件", lambda: check_references(skill_dir)),
        ("模板文件", lambda: check_templates(skill_dir)),
        ("脚本文件", lambda: check_scripts(skill_dir)),
        ("脚本语法", lambda: check_svg_to_png_syntax()),
    ]

    passed = 0
    total = len(checks)
    for name, check_fn in checks:
        print(f"\n[{name}]")
        if check_fn():
            passed += 1

    return passed, total


def run_golden_cases(skill_dir: Path) -> Tuple[int, int]:
    """运行金用例检查，返回 (通过数, 总数)。"""
    print()
    print("=" * 50)
    print("金用例检查")
    print("=" * 50)

    cases = [
        {
            "name": "调性目录完整性",
            "check": lambda: check_tone_catalog(skill_dir),
        },
        {
            "name": "配色目录完整性",
            "check": lambda: check_palette_catalog(skill_dir),
        },
        {
            "name": "封面公式完整性",
            "check": lambda: check_cover_formulas(skill_dir),
        },
    ]

    passed = 0
    total = len(cases)
    for case in cases:
        print(f"\n[{case['name']}]")
        if case["check"]():
            passed += 1

    return passed, total


def check_tone_catalog(skill_dir: Path) -> bool:
    """检查调性目录是否包含所有 9 种调性。"""
    content = (skill_dir / "references" / "visual-system.md").read_text(encoding="utf-8")
    tones = ["治愈系", "高级感", "干货风", "活泼风", "文艺风", "极简风", "复古风", "纯欲风", "科技风"]
    missing = [t for t in tones if t not in content]
    if not missing:
        print(f"  [OK] 调性目录包含全部 {len(tones)} 种调性")
        return True
    else:
        print(f"  [FAIL] 缺少调性: {', '.join(missing)}")
        return False


def check_palette_catalog(skill_dir: Path) -> bool:
    """检查配色目录是否包含足够的配色方案。"""
    content = (skill_dir / "references" / "visual-system.md").read_text(encoding="utf-8")
    palettes = ["cream", "morandi", "macaron", "jewel", "grey-luxe", "cool",
                "editorial", "ink", "earth", "vintage", "pink-soft", "tech", "pop", "mono"]
    found = [p for p in palettes if p in content]
    if len(found) >= 10:
        print(f"  [OK] 配色目录包含 {len(found)}/{len(palettes)} 套方案")
        return True
    else:
        print(f"  [FAIL] 配色方案不足: 仅找到 {len(found)}/{len(palettes)}")
        return False


def check_cover_formulas(skill_dir: Path) -> bool:
    """检查封面公式是否完整。"""
    content = (skill_dir / "references" / "visual-system.md").read_text(encoding="utf-8")
    formulas = ["大字报", "对比", "清单", "数字冲击", "Before-After", "人物金句", "提问式", "测评打分"]
    missing = [f for f in formulas if f not in content]
    if not missing:
        print(f"  [OK] 封面公式包含全部 {len(formulas)} 种")
        return True
    else:
        print(f"  [FAIL] 缺少封面公式: {', '.join(missing)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="redbook-content-skill 评估运行器")
    parser.add_argument("skill_dir", type=Path, help="技能目录路径")
    parser.add_argument("--validate", action="store_true", help="仅运行结构验证")
    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"错误：{args.skill_dir} 不是有效目录")
        sys.exit(1)

    print(f"评估技能: {args.skill_dir.name}")
    print()

    passed, total = run_structure_checks(args.skill_dir)

    if not args.validate:
        g_passed, g_total = run_golden_cases(args.skill_dir)
        passed += g_passed
        total += g_total

    print()
    print("=" * 50)
    print(f"结果: {passed}/{total} 通过")
    print("=" * 50)

    if passed == total:
        print("VALID")
        sys.exit(0)
    else:
        print("INVALID — 有检查未通过")
        sys.exit(1)


if __name__ == "__main__":
    main()
