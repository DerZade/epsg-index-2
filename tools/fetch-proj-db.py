#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Download the newest PROJ database into .proj-data/.

pyproj wheels bundle whichever proj.db was current when their PROJ build was
made, which lags the EPSG registry by a lot (pyproj 3.7.2 ships PROJ 9.5.1 with
EPSG v11.022 from 2024-11-05). update-index.py prefers the newest proj.db it can
find, so fetching a fresh one here keeps the index from freezing on the wheel's
snapshot.

The database is taken from the conda-forge `proj` package, because that is the
only place PROJ's data directory is published as a ready-made download. proj.db
is a plain SQLite file and platform independent, so the linux-64 build is used
everywhere.
"""

import io
import json
import os
import shutil
import sqlite3
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / '.proj-data'
STAMP_FILE = OUT_DIR / '.package'
API_URL = 'https://api.anaconda.org/package/conda-forge/proj'
CHANNEL_URL = 'https://conda.anaconda.org/conda-forge'
SUBDIR = 'linux-64'


def newest_package() -> dict:
    """Return the conda-forge `proj` file with the highest version."""
    with urllib.request.urlopen(API_URL) as response:
        files = json.load(response)['files']

    candidates = [
        f
        for f in files
        if f['attrs'].get('subdir') == SUBDIR
        and f['basename'].endswith('.conda')
        and 'broken' not in f.get('labels', [])
    ]
    if not candidates:
        sys.exit(f'No conda-forge proj package found for {SUBDIR}')

    def sort_key(f: dict) -> tuple:
        version = tuple(int(p) if p.isdigit() else 0 for p in f['version'].split('.'))
        return version, f['attrs'].get('build_number', 0), f['upload_time']

    return max(candidates, key=sort_key)


def decompress_zstd(data: bytes) -> bytes:
    try:
        from compression import zstd  # Python 3.14+
    except ImportError:
        pass
    else:
        return zstd.decompress(data)

    try:
        import zstandard  # optional dependency
    except ImportError:
        pass
    else:
        return zstandard.ZstdDecompressor().decompress(data, max_output_size=512 << 20)

    zstd_binary = shutil.which('zstd')
    if zstd_binary is None:
        sys.exit(
            'Cannot decompress the package: need Python 3.14+, the zstandard '
            'package (pip install zstandard) or the zstd command line tool.'
        )

    import subprocess

    return subprocess.run(
        [zstd_binary, '-d', '-c'], input=data, stdout=subprocess.PIPE, check=True
    ).stdout


def extract_proj_data(package: bytes, out_dir: Path) -> None:
    """Extract share/proj/* out of a .conda package into out_dir."""
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        inner = next(
            name
            for name in archive.namelist()
            if name.startswith('pkg-') and name.endswith('.tar.zst')
        )
        payload = decompress_zstd(archive.read(inner))

    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(payload)) as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.startswith('share/proj/'):
                continue
            member.name = os.path.basename(member.name)
            tar.extract(member, out_dir, filter='data')


def database_metadata(data_dir: Path) -> dict[str, str]:
    connection = sqlite3.connect(f'file:{data_dir / "proj.db"}?mode=ro', uri=True)
    try:
        return dict(connection.execute('SELECT key, value FROM metadata').fetchall())
    finally:
        connection.close()


def main() -> None:
    package = newest_package()
    basename = os.path.basename(package['basename'])

    if STAMP_FILE.is_file() and STAMP_FILE.read_text().strip() == basename and (OUT_DIR / 'proj.db').is_file():
        metadata = database_metadata(OUT_DIR)
        print(f'{OUT_DIR} is already up to date ({basename}, EPSG {metadata["EPSG.VERSION"]})')
        return

    url = f'{CHANNEL_URL}/{package["basename"]}'
    print(f'Downloading {url}')
    with urllib.request.urlopen(url) as response:
        payload = response.read()

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / 'proj'
        extract_proj_data(payload, staging)
        if not (staging / 'proj.db').is_file():
            sys.exit(f'{basename} does not contain share/proj/proj.db')
        metadata = database_metadata(staging)
        shutil.rmtree(OUT_DIR, ignore_errors=True)
        shutil.move(staging, OUT_DIR)

    STAMP_FILE.write_text(f'{basename}\n')
    print(
        f'Wrote {OUT_DIR} from {basename} '
        f'(PROJ {metadata["PROJ.VERSION"]}, EPSG dataset {metadata["EPSG.VERSION"]} ({metadata["EPSG.DATE"]}))'
    )


if __name__ == '__main__':
    sys.exit(main())
