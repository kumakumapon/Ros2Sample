"""Regression tests for scripts/check_docs_consistency.py."""

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_docs_consistency as checker  # noqa: E402


class ConsoleScriptNamesTest(unittest.TestCase):
    def test_handles_adjacent_string_literals(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_py = Path(temp_dir) / 'setup.py'
            setup_py.write_text(
                "from setuptools import setup\n"
                "setup(entry_points={'console_scripts': [\n"
                "    'wrapped_node = ' 'package.wrapped:main',\n"
                "    'plain_node = package.plain:main',\n"
                "]})\n",
                encoding='utf-8',
            )

            self.assertEqual(
                checker.console_script_names(setup_py),
                ['wrapped_node', 'plain_node'],
            )

    def test_split_entry_point_missing_from_readme_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / 'example_package'
            package_dir.mkdir()
            (package_dir / 'setup.py').write_text(
                "from setuptools import setup\n"
                "setup(entry_points={'console_scripts': [\n"
                "    'undocumented_node = ' 'package.node:main',\n"
                "]})\n",
                encoding='utf-8',
            )
            (package_dir / 'README.md').write_text(
                '# Example package\n', encoding='utf-8')

            errors = []
            checker.check_executables_documented([package_dir], errors)

            self.assertEqual(
                errors,
                ['example_package: 実行ファイル `undocumented_node` が'
                 'パッケージ README で言及されていません'],
            )


class PackageReadmeTest(unittest.TestCase):
    def test_missing_readme_is_reported_for_executable_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / 'example_package'
            package_dir.mkdir()
            (package_dir / 'setup.py').write_text(
                "from setuptools import setup\nsetup()\n", encoding='utf-8')

            errors = []
            checker.check_executables_documented([package_dir], errors)

            self.assertEqual(
                errors, ['example_package: パッケージ README.md がありません'])

    def test_only_declared_rosidl_interface_package_is_exempt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / 'sample_interfaces'
            package_dir.mkdir()
            (package_dir / 'package.xml').write_text(
                '<package><member_of_group>rosidl_interface_packages'
                '</member_of_group></package>',
                encoding='utf-8',
            )

            errors = []
            checker.check_executables_documented([package_dir], errors)

            self.assertEqual(errors, [])

    def test_listed_interface_package_without_marker_is_not_exempt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / 'sample_interfaces'
            package_dir.mkdir()
            (package_dir / 'package.xml').write_text(
                '<package/>', encoding='utf-8')

            errors = []
            checker.check_executables_documented([package_dir], errors)

            self.assertEqual(
                errors, ['sample_interfaces: パッケージ README.md がありません'])


class RootInventoryTest(unittest.TestCase):
    def test_executable_in_other_package_does_not_hide_missing_row(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / 'src' / 'demo'
            pkg.mkdir(parents=True)
            (pkg / 'setup.py').write_text(
                "from setuptools import setup\n"
                "setup(entry_points={'console_scripts': ['node = demo.node:main']})\n")
            for filename in ('README.md', 'README.en.md'):
                (pkg / filename).write_text('# Demo\n')
                (root / filename).write_text(
                    f'[demo](src/demo/{filename})\n'
                    '| `demo` | no executable |\n'
                    '| `other` | `node` |\n')
            errors = []
            with patch.object(checker, 'REPO_ROOT', root):
                checker.check_root_inventory([pkg], errors)
            self.assertEqual(len(errors), 2)
            self.assertTrue(all('missing executable node' in e for e in errors))

    def test_missing_tutorial_is_reported(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tutorials = root / 'docs/tutorials'
            (tutorials / 'en').mkdir(parents=True)
            (tutorials / '24_new.md').write_text('# New chapter\n')
            (tutorials / 'en/00_learning_path.md').write_text('# Path\n')
            (root / 'README.md').write_text('# Root\n')
            errors = []
            with patch.object(checker, 'REPO_ROOT', root):
                checker.check_tutorial_index(errors)
            self.assertEqual(len(errors), 2)
            self.assertTrue(all('24_new.md' in e for e in errors))

    def test_broken_local_link_is_reported_but_external_link_is_ignored(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'README.md').write_text(
                '[missing](missing.md) [web](https://example.com) [anchor](#intro)\n')
            errors = []
            with patch.object(checker, 'REPO_ROOT', root):
                checker.check_entry_links([], errors)
            self.assertEqual(errors, ['README.md: broken link missing.md'])


if __name__ == '__main__':
    unittest.main()
