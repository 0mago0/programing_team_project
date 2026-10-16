"""Package the edited A submission without regenerating personal records."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'deliverables' / 'A_第5週繳交包_五人版'
archive = source.with_suffix('.zip')
if not source.is_dir():
    raise SystemExit('找不到 A 繳交資料夾')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(source.rglob('*')):
        if path.is_file() and not {'__pycache__', '.pytest_cache'} & set(path.parts):
            z.write(path, path.relative_to(source.parent))
with zipfile.ZipFile(archive) as z:
    bad = z.testzip()
    if bad:
        raise RuntimeError(f'ZIP 驗證失敗: {bad}')
    print(f'ZIP verified: {len(z.namelist())} files')
