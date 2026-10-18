import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class DispatchTest(unittest.TestCase):
    def invoke(self, repository, mode='ci', tag=''):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/dispatch_jafly.py'), '--trigger-repo', repository, '--mode', mode, '--release-tag', tag, '--dry-run'], capture_output=True, text=True)

    def test_java_trigger_dispatches_one_reactor(self):
        for repository in ['fireflyframework-parent', 'fireflyframework-agentic-bridge', 'fireflyframework-jafly']:
            with self.subTest(repository=repository):
                result = self.invoke(repository)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), ['gh', 'workflow', 'run', 'ci.yml', '--repo', 'fireflyframework/fireflyframework-jafly', '--ref', 'develop'])

    def test_python_and_other_frameworks_cannot_trigger_java(self):
        for repository in ['fireflyframework-agentic', 'fireflyframework-datascience', 'fireflyframework-pyfly', 'fireflyframework-php', 'fireflyframework-rust', 'fireflyframework-dotnet', 'fireflyframework-go', 'secrets-vault']:
            with self.subTest(repository=repository):
                result = self.invoke(repository)
                self.assertNotEqual(result.returncode, 0)

    def test_release_requires_existing_final_tag(self):
        for tag in ['', 'main', 'v26.10.17-SNAPSHOT', 'v26.1.7']:
            with self.subTest(tag=tag):
                self.assertNotEqual(self.invoke('fireflyframework-jafly', 'release', tag).returncode, 0)
        result = self.invoke('fireflyframework-jafly', 'release', 'v26.10.17')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ['gh', 'workflow', 'run', 'release.yml', '--repo', 'fireflyframework/fireflyframework-jafly', '--ref', 'v26.10.17', '-f', 'tag=v26.10.17'])


if __name__ == '__main__':
    unittest.main()
