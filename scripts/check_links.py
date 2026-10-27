"""Check file targets in ordinary Markdown links, without third-party packages."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parents[1]
errors = []
count = 0
for path in root.rglob('*.md'):
    if '.git' in path.parts or ('inbox' in path.parts and path.name != 'README.md'):
        continue
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'^```.*?^```[^\n]*', '', text, flags=re.M | re.S)
    for match in re.finditer(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text):
        target = match.group(1).strip('<>')
        parsed = urlsplit(target)
        if parsed.scheme or not parsed.path:
            continue
        count += 1
        if not (path.parent / unquote(parsed.path)).resolve().is_file():
            errors.append(f'{path.relative_to(root)}: {target}')
for error in errors:
    print(error)
print(f'Checked {count} local file links; {len(errors)} missing targets.')
raise SystemExit(bool(errors))
