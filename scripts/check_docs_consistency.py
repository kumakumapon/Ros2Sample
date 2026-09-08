#!/usr/bin/env python3
"""Consistency checker between documentation and implementation.

Compares the actual ROS 2 packages under ``src/`` against the root
README and the specification docs, and exits non-zero when they have
drifted apart. Intended to run in CI as
``python3 scripts/check_docs_consistency.py``.

Checks:

1. Every package under ``src/`` (a directory with package.xml) is
   listed in the root README.md; simulation packages must also appear
   in docs/simulation_spec.md.
2. Every ``config/*.yaml`` in a package is referenced from a launch
   file or the package README (detects unwired "orphan" configs).
3. Every executable registered in setup.py ``console_scripts`` is
   mentioned in the package README.
4. Root README rows and links cover executables, packages and tutorials in
   both languages; foundational English chapters and local entry links exist.
"""

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / 'src'

# チュートリアル用パッケージなど、シミュレーション仕様書
# (docs/simulation_spec.md) への記載を必須としないパッケージ。
SPEC_EXEMPT_PACKAGES = {'ros2_learning', 'ros2_learning_cpp'}

# README を持たないことを許容するのは、ROS 2 のインターフェース定義だけを
# 提供するパッケージに限る。名前をこのリストに追加するだけでは除外されず、
# package.xml の rosidl_interface_packages 宣言も必要とする。
INTERFACE_ONLY_PACKAGES = {'sample_interfaces'}
INTERFACE_PACKAGE_MARKER = '<member_of_group>rosidl_interface_packages</member_of_group>'


def find_packages():
    """Return the directories under src/ that contain a package.xml."""
    return sorted(
        p.parent for p in SRC_DIR.glob('*/package.xml')
    )


def check_package_listed(pkg_dirs, errors):
    """Check that every package is listed in the README and the spec."""
    readme = (REPO_ROOT / 'README.md').read_text(encoding='utf-8')
    spec = (REPO_ROOT / 'docs' / 'simulation_spec.md').read_text(
        encoding='utf-8')
    for pkg_dir in pkg_dirs:
        name = pkg_dir.name
        if f'`{name}`' not in readme:
            errors.append(
                f'README.md: パッケージ `{name}` が記載されていません')
        if name in SPEC_EXEMPT_PACKAGES:
            continue
        if f'`{name}`' not in spec:
            errors.append(
                f'docs/simulation_spec.md: パッケージ `{name}` が'
                '収録パッケージとして記載されていません')


def check_config_referenced(pkg_dirs, errors):
    """Check that every config/*.yaml is referenced by launch or README."""
    for pkg_dir in pkg_dirs:
        config_dir = pkg_dir / 'config'
        if not config_dir.is_dir():
            continue
        references = ''
        for launch_file in pkg_dir.glob('launch/*.py'):
            references += launch_file.read_text(encoding='utf-8')
        pkg_readme = pkg_dir / 'README.md'
        if pkg_readme.is_file():
            references += pkg_readme.read_text(encoding='utf-8')
        for yaml_file in sorted(config_dir.glob('*.yaml')):
            if yaml_file.name not in references:
                errors.append(
                    f'{pkg_dir.name}: config/{yaml_file.name} が launch '
                    'ファイルからもパッケージ README からも参照されていません')


def console_script_names(setup_py):
    """Return console_scripts names declared by a literal setup() call.

    Parsing Python instead of scanning text also handles adjacent string
    literals, which are commonly used to wrap long entry-point declarations.
    """
    tree = ast.parse(
        setup_py.read_text(encoding='utf-8'), filename=str(setup_py))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function_name = (
            node.func.id if isinstance(node.func, ast.Name)
            else node.func.attr if isinstance(node.func, ast.Attribute)
            else None
        )
        if function_name != 'setup':
            continue
        for keyword in node.keywords:
            if keyword.arg != 'entry_points':
                continue
            entry_points = ast.literal_eval(keyword.value)
            console_scripts = entry_points.get('console_scripts', [])
            return [entry_point.partition('=')[0].strip()
                    for entry_point in console_scripts]
    return []


def is_interface_only_package(pkg_dir):
    """Return whether a documented README exclusion is valid for a package."""
    if pkg_dir.name not in INTERFACE_ONLY_PACKAGES:
        return False
    package_xml = pkg_dir / 'package.xml'
    return (package_xml.is_file() and INTERFACE_PACKAGE_MARKER in
            package_xml.read_text(encoding='utf-8'))


def check_executables_documented(pkg_dirs, errors):
    """Check that every console_scripts executable is documented."""
    for pkg_dir in pkg_dirs:
        setup_py = pkg_dir / 'setup.py'
        pkg_readme = pkg_dir / 'README.md'
        if not pkg_readme.is_file():
            if not is_interface_only_package(pkg_dir):
                errors.append(f'{pkg_dir.name}: パッケージ README.md がありません')
            continue
        if not setup_py.is_file():
            continue
        readme_text = pkg_readme.read_text(encoding='utf-8')
        for executable in console_script_names(setup_py):
            if executable not in readme_text:
                errors.append(
                    f'{pkg_dir.name}: 実行ファイル `{executable}` が'
                    'パッケージ README で言及されていません')


def check_root_inventory(pkg_dirs, errors):
    """Check per-package executable rows and README links in both entry points."""
    for filename in ('README.md', 'README.en.md'):
        readme = REPO_ROOT / filename
        if not readme.is_file():
            errors.append(f'{filename}: missing root README')
            continue
        text = readme.read_text(encoding='utf-8')
        for pkg in pkg_dirs:
            if is_interface_only_package(pkg):
                continue
            suffix = 'README.en.md' if filename.endswith('.en.md') else 'README.md'
            target = f'src/{pkg.name}/{suffix}'
            if f']({target})' not in text:
                errors.append(f'{filename}: missing package link {target}')
            if not (pkg / suffix).is_file():
                errors.append(f'{pkg.name}: missing {suffix}')
            setup_py = pkg / 'setup.py'
            if not setup_py.is_file():
                continue
            rows = [line for line in text.splitlines()
                    if line.startswith(f'| `{pkg.name}` |')]
            row = '\n'.join(rows)
            for name in console_script_names(setup_py):
                if f'`{name}`' not in row:
                    errors.append(f'{filename}: {pkg.name} missing executable {name}')


def check_tutorial_index(errors):
    """Require every Japanese chapter in the root index and the English route."""
    root = (REPO_ROOT / 'README.md').read_text(encoding='utf-8')
    english_path = REPO_ROOT / 'docs/tutorials/en/00_learning_path.md'
    if not english_path.is_file():
        errors.append('Missing English learning path')
        return
    english = english_path.read_text(encoding='utf-8')
    for chapter in sorted((REPO_ROOT / 'docs/tutorials').glob('[0-9][0-9]_*.md')):
        if f'](docs/tutorials/{chapter.name})' not in root:
            errors.append(f'README.md: missing tutorial {chapter.name}')
        if chapter.name not in english:
            errors.append(f'English learning path: missing tutorial {chapter.name}')
        if int(chapter.name[:2]) <= 6:
            if not (chapter.parent / 'en' / chapter.name).is_file():
                errors.append(f'Missing foundational English chapter {chapter.name}')


def check_entry_links(pkg_dirs, errors):
    """Validate local Markdown links in the maintained entry-point documents."""
    docs = list(REPO_ROOT.glob('README*.md'))
    docs += list((REPO_ROOT / 'docs/tutorials/en').glob('*.md'))
    for pkg in pkg_dirs:
        docs += list(pkg.glob('README*.md'))
    for doc in docs:
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            path = target.split('#', 1)[0]
            if path and not (doc.parent / path).exists():
                errors.append(f'{doc.relative_to(REPO_ROOT)}: broken link {target}')


def main():
    """Run all checks and return 1 when any drift is found."""
    pkg_dirs = find_packages()
    if not pkg_dirs:
        print('src/ 配下に ROS 2 パッケージが見つかりません', file=sys.stderr)
        return 1
    errors = []
    check_package_listed(pkg_dirs, errors)
    check_config_referenced(pkg_dirs, errors)
    check_executables_documented(pkg_dirs, errors)
    check_root_inventory(pkg_dirs, errors)
    check_tutorial_index(errors)
    check_entry_links(pkg_dirs, errors)
    if errors:
        print('ドキュメントと実装の乖離が見つかりました:', file=sys.stderr)
        for error in errors:
            print(f'  - {error}', file=sys.stderr)
        return 1
    print(f'OK: {len(pkg_dirs)} パッケージのドキュメント整合性を確認しました')
    return 0


if __name__ == '__main__':
    sys.exit(main())
