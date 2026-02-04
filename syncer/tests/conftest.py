# fixtures here will be reusable by all tests
import pytest
from pathlib import Path
from shutil import copy2

from .. scanner import Scanner, Strategy

ASSETS_DIR = Path('syncer', 'tests', 'assets')

@pytest.fixture(scope="session")
def source_dir(tmp_path_factory):
    srcdir = tmp_path_factory.mktemp('source')
    (srcdir / 'samedir').mkdir()

    createdir = srcdir / 'createdir'
    createdir.mkdir()
    (createdir / 'addfile_indir.txt').touch()

    dirandfile = srcdir / 'yeah'
    dirandfile.mkdir()
    (dirandfile / 'new.txt').touch()
    (dirandfile / 'new.txt').write_text('test1')

    copy2(ASSETS_DIR / 'modified.jpg', srcdir)
    copy2(ASSETS_DIR / 'same.jpg', srcdir)
    copy2(ASSETS_DIR / 'Screenshot 2025-11-11 183727.png', srcdir) # missing, to be copied

    # for POSIX OS's only (Linux/Mac)
    norights = (srcdir / 'norights.txt')
    norights.touch()
    norights.chmod(0o044) # should be un-readable/copy-able

    return srcdir


@pytest.fixture(scope="session")
def target_dir(tmp_path_factory):
    tgtdir = tmp_path_factory.mktemp('target')
    (tgtdir / 'samedir').mkdir()

    deldir = tgtdir / 'deldir'
    (deldir / '1').mkdir(parents=True)
    (deldir / 'delfile_indir.txt').touch()

    copy2(ASSETS_DIR / 'modified_.jpg', tgtdir / 'modified.jpg')
    copy2(ASSETS_DIR / 'same.jpg', tgtdir)
    (tgtdir / 'yeah').touch() # file in target, dir in source

    return tgtdir


@pytest.fixture
def diff_obj_generator(source_dir, target_dir):
    scanner = Scanner(source_dir, target_dir, Strategy.HASH)
    return scanner.run()
