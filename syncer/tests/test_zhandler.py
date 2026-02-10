import pytest
from pathlib import Path

from .. handler import execute_filesystem

# pytest syncer\tests\test_zhandler.py -v -s

def test_copy_items_threaded(diff_obj_generator, target_dir):
    execute_filesystem(diff_obj_generator, False, False, workers=4)

    assert Path(target_dir, 'createdir').is_dir()
    assert Path(target_dir, 'Screenshot 2025-11-11 183727.png').is_file()

def test_replace_items(diff_obj_generator, target_dir, source_dir):
    mtime = Path(target_dir, 'modified.jpg').stat().st_mtime
    assert Path(target_dir, 'modified.jpg').is_file()

    assert Path(target_dir, 'yeah').is_file() # file in target

    execute_filesystem(diff_obj_generator, True, False, None) # replaces allowed

    assert Path(target_dir, 'modified.jpg').is_file()
    mtime_new = Path(target_dir, 'modified.jpg').stat().st_mtime
    assert mtime != mtime_new

    # test that source folder structure replaces target file
    assert Path(target_dir, 'yeah').is_dir() # now dir in target
    children = Path(target_dir, 'yeah').iterdir()
    assert len(list(children)) > 0 # children copied as well

def test_delete_items(diff_obj_generator, target_dir):
    assert Path(target_dir, 'deldir').exists()

    execute_filesystem(diff_obj_generator, False, True, None) # deletes allowed

    assert Path(target_dir, 'deldir', 'delfile_indir.txt').exists() == False
    assert Path(target_dir, 'deldir', '1').exists() == False
    assert Path(target_dir, 'deldir').exists() == False
