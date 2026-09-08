"""Regression tests for loading the built workspace before colcon test discovery."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class LintEnvironmentTest(unittest.TestCase):
    """Exercise the real lint script with a controlled colcon executable."""

    def run_lint(self, with_overlay):
        """Run in an isolated workspace whose colcon requires the overlay marker."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'bin').mkdir()
            shutil.copyfile(Path(__file__).with_name('lint.sh'), root / 'scripts/lint.sh')
            (root / 'scripts/xml-catalog.sh').write_text('# No XML catalog needed here.\n')
            if with_overlay:
                (root / 'install').mkdir()
                (root / 'install/setup.bash').write_text('export LINT_TEST_OVERLAY=loaded\n')
            colcon = root / 'bin/colcon'
            colcon.write_text(
                '#!/usr/bin/env bash\n'
                '[[ "${LINT_TEST_OVERLAY:-}" == loaded ]] || exit 42\n'
                'case "$1" in\n'
                '  list) echo sample_utils ;;\n'
                '  test) echo "tested with overlay" ;;\n'
                '  *) exit 43 ;;\n'
                'esac\n')
            colcon.chmod(0o755)
            environment = os.environ.copy()
            environment.pop('LINT_TEST_OVERLAY', None)
            environment['PATH'] = str(root / 'bin') + os.pathsep + environment['PATH']
            return subprocess.run(
                ['bash', 'scripts/lint.sh'], cwd=root, env=environment,
                capture_output=True, text=True, timeout=10)

    def test_overlay_precedes_discovery_and_tests(self):
        """Both discovery and test execution must see the sourced overlay."""
        result = self.run_lint(with_overlay=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('tested with overlay', result.stdout)

    def test_missing_build_is_reported(self):
        """A missing overlay must fail with an actionable build instruction."""
        result = self.run_lint(with_overlay=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Run scripts/build.sh first', result.stderr)


if __name__ == '__main__':
    unittest.main()
