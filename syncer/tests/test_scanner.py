import pytest
from pathlib import Path
from .. scanner import Scanner, Strategy

""" Test cases:

Failures:
- Instantiation: missing / wrong Strategy
- Missing source/target directory
- !! no rights to access file (get_hash)
- currently open file
- corrupted file

Integration:
- same contents output nothing (notify user no action)
- compare changed file
- check if superfluous files in target are marked for deletion
- whole directory missing (analyze actions taken)
- whole directory RENAMED only (what happens? - delete + copytree?)
- integration test with temp directories ?? - clarify
- large files (>300 MB ?)

"""

testfile = Path(r"C:\Personal\Downloads\Python\screens\norights.txt")

@pytest.fixture
def source_dir():
    return Path(r"C:\Personal\Downloads\Python\screens")

@pytest.fixture
def target_dir():
    return Path("syncer\\target")


def test_instantiation(source_dir, target_dir):
    comparison_strategy = 'test'
    with pytest.raises(KeyError):
        scanner = Scanner(source_dir, target_dir, comparison_strategy)

# def test_missing_dir(source_dir, target_dir):
#     pass # cannot test this, because it is plopped in main

def test_access_rights_copy(source_dir, target_dir):
    scanner = Scanner(source_dir, target_dir, Strategy.HASH)
    assert scanner.compare_files(testfile, testfile) == True

def test_access_rights_hash():
    with pytest.raises(PermissionError):
        Scanner.get_hash(testfile)