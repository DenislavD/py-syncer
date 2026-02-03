import pytest
from pathlib import Path
from shutil import copy2
from pprint import pprint
from .. scanner import Scanner, Strategy

""" Test cases:

Integration:
- compare changed file
- check if superfluous files in target are marked for deletion
- whole directory missing (analyze actions taken)
- whole directory RENAMED only (what happens? - delete + copytree?)
- integration test with temp directories ?? - clarify
- large files (>300 MB ?)
- same contents output nothing (notify user no action)

"""

TESTFILE = Path(r"C:\Personal\Downloads\Python\screens\norights.txt")
TESTSOURCE = Path(r"C:\Personal\Downloads\Python\screens")
TESTTARGET = Path('syncer', 'logs')
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


# def test_incorrect_cli_arg_dir():
#     pass # cannot test this, because it is plopped in main

def test_instantiation():
    comparison_strategy = 'test'
    with pytest.raises(KeyError):
        scanner = Scanner(TESTSOURCE, TESTTARGET, comparison_strategy)

def test_access_rights_copy():
    # needs to skip files -> comparison to return True
    scanner = Scanner(TESTSOURCE, TESTTARGET, Strategy.HASH)
    assert scanner.compare_files(TESTFILE, TESTFILE) == True

def test_access_rights_hash():
    with pytest.raises(PermissionError):
        Scanner.get_hash(TESTFILE)

def test_comparison_tmpdir(source_dir, target_dir):
    scanner = Scanner(source_dir, target_dir, Strategy.STATS)

    result = {}
    for diff in scanner.run():
        result.setdefault(diff.Action, []).append(diff.target.relative_to(target_dir))
    #pprint(result)

    # should delete items in order starting from the deepest level
    assert result['delete'] == [
        Path('deldir', 'delfile_indir.txt'),
        Path('deldir', '1'),
        Path('deldir')
    ]

    # should replace the following items
    assert Path('modified.jpg') in result['replace']
    assert Path('yeah') in result['replace']

    # should just copy the following items
    assert Path('createdir') in result['copy']
    assert Path('Screenshot 2025-11-11 183727.png') in result['copy']


# def test_fixtures(source_dir, target_dir):
#     # test only: pytest -s -k test_fixtures
#     print(f'Received source dir: {source_dir}')
#     for child in source_dir.iterdir():
#         print(child)
#     print(f'Received target dir: {target_dir}')
#     for child in target_dir.iterdir():
#         print(child)
#     assert 1 == 1


