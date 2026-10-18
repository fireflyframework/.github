#!/usr/bin/env python3
"""Route former Java source triggers to one reactor; report dispatch separately."""
import argparse
import json
import pathlib
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trigger-repo', required=True)
    parser.add_argument('--mode', choices=['ci', 'release'], default='ci')
    parser.add_argument('--release-tag', default='')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    sources = json.loads((root / 'docs/jafly-source-repositories.json').read_text())
    if args.trigger_repo not in {*sources, 'fireflyframework-jafly'}:
        parser.error('Trigger must be Jafly or one of its former Java source repositories')
    workflow, ref = 'ci.yml', 'develop'
    if args.mode == 'release':
        if not re.fullmatch(r'v\d{2}\.\d{2}\.\d{2}', args.release_tag):
            parser.error('Release mode requires an existing final tag such as v26.10.17')
        workflow, ref = 'release.yml', args.release_tag
    command = ['gh', 'workflow', 'run', workflow, '--repo', 'fireflyframework/fireflyframework-jafly', '--ref', ref]
    if args.mode == 'release':
        command += ['-f', 'tag=' + ref]
    if args.dry_run:
        print(json.dumps(command))
    else:
        subprocess.run(command, check=True)
        print(f'Dispatched {workflow} at {ref}. Destination validation runs separately: https://github.com/fireflyframework/fireflyframework-jafly/actions')


if __name__ == '__main__':
    main()
