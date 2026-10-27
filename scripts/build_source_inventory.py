"""Capture Markdown source paths once; preserve subsequent migration decisions."""
import csv
import subprocess
import sys
from pathlib import Path

source = Path(sys.argv[1]).resolve()
target = Path(__file__).resolve().parents[1] / 'migration' / 'source-inventory.csv'
if target.exists():
    raise SystemExit('Inventory already exists; refusing to overwrite migration decisions.')

def git(*args):
    return subprocess.check_output(['git', '-C', str(source), *args]).decode('utf-8').strip()

def stage(path):
    parts = path.lower()
    if any(x in parts for x in ['/linux/', '/containers/', '/observability/', '/production/', '/контейнеризация']):
        return 'os-or-operations'
    if '/go/' in parts:
        return 'go'
    if any(x in parts for x in ['/networking/', '/сети/']):
        return 'networking'
    if any(x in parts for x in ['/databases/', '/база данных/']):
        return 'databases'
    if any(x in parts for x in ['/messaging/', '/distributed-systems/', '/брокеры сообщений/']):
        return 'distributed-systems'
    if '/algorithms/' in parts:
        return 'algorithms'
    if '/security/' in parts:
        return 'security'
    return 'navigation-or-cross-topic'

with target.open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=['revision', 'path', 'stage', 'status', 'target', 'decision'])
    writer.writeheader()
    count = 0
    for revision in ['cc2e017', '8c3e245']:
        sha = git('rev-parse', revision)
        for path in git('-c', 'core.quotepath=false', 'ls-tree', '-r', '--name-only', sha).splitlines():
            if not path.endswith('.md'):
                continue
            if revision == '8c3e245' and not path.startswith('docs/'):
                continue
            writer.writerow(dict(revision=sha, path=path, stage=stage(path), status='pending', target='', decision=''))
            count += 1
print(f'Captured {count} Markdown source candidates.')
