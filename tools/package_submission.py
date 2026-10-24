"""Package the edited A submission without regenerating personal records.

用法：python tools/package_submission.py [deliverables 內的資料夾名稱]
未指定時打包第 5 週繳交包。
"""
from pathlib import Path
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv) > 1 else 'A_第5週繳交包_五人版'
source = root / 'deliverables' / name
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
