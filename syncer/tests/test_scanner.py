import pytest
from pathlib import Path

from .. scanner import Scanner, Strategy

# Missing a large file test (300MB) and no permissions on Linux (how?)

TESTFILE = Path(r"C:\Personal\Downloads\Python\screens\norights.txt")
TESTTARGET = Path('syncer', 'logs')
ASSETS_DIR = Path('syncer', 'tests', 'assets')


def test_incorrect_cli_arg_dir():
    pass # cannot test this, because it is plopped in main

def test_instantiation():
    comparison_strategy = 'test'
    with pytest.raises(KeyError):
        scanner = Scanner(ASSETS_DIR, TESTTARGET, comparison_strategy)

def test_access_rights_hash():
    with pytest.raises(PermissionError):
        Scanner.get_hash(TESTFILE)

def test_access_rights_copy():
    # needs to skip files -> comparison to return True
    scanner = Scanner(ASSETS_DIR, TESTTARGET, Strategy.HASH)
    assert scanner.compare_files(TESTFILE, TESTFILE) == True

def test_comparison_same_dir(source_dir):
    scanner = Scanner(source_dir, source_dir)
    gen = scanner.run()
    assert len(list(gen)) == 0

def test_comparison_tmpdir(source_dir, target_dir):
    scanner = Scanner(source_dir, target_dir, Strategy.HASH)

    actions = {}
    for diff in scanner.run():
        actions.setdefault(diff.Action, []).append(diff.target.relative_to(target_dir))

    # should delete items in order starting from the deepest level
    assert actions['delete'] == [
        Path('deldir')
    ]
    
    # should replace the following items
    assert Path('modified.jpg') in actions['replace']
    assert Path('yeah') in actions['replace']

    # should just copy the following items
    assert Path('createdir') in actions['copy']
    assert Path('Screenshot 2025-11-11 183727.png') in actions['copy']

def test_exclude_pattern():
    files = Scanner.get_items_in_dir(Path('.'), exclude='.git|__pycache__|logs|venv|README.md')

    assert all('.git' not in str(file) for file in files)
    assert all('logs' not in str(file) for file in files)
    assert all('venv' not in str(file) for file in files)
    assert all('README.md' not in str(file) for file in files)



# def test_fixtures(source_dir, target_dir):
#     # test only: pytest -s -k test_fixtures
#     print(f'Received source dir: {source_dir}')
#     for child in source_dir.iterdir():
#         print(child)
#     print(f'Received target dir: {target_dir}')
#     for child in target_dir.iterdir():
#         print(child)
#     assert 1 == 1


""" actions dict for reference:

{<Action.COPY: 'copy'>: [WindowsPath('createdir'),                                                                                                                                                         
                         WindowsPath('norights.txt'),                                                                                                                                                                                   
                         WindowsPath('Screenshot 2025-11-11 183727.png'),                                                                                                                                                               
                         WindowsPath('yeah/new.txt')],                                                                                                                                                                                  
 <Action.DELETE: 'delete'>: [WindowsPath('deldir/delfile_indir.txt'),                                                                                                                                                                   
                             WindowsPath('deldir/1'),                                                                                                                                                                                   
                             WindowsPath('deldir')],                                                                                                                                                                                    
 <Action.REPLACE: 'replace'>: [WindowsPath('modified.jpg'),                                                                                                                                                                             
                               WindowsPath('yeah')]} 
"""
