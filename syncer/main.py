# here I will implement the project\
import os
from pathlib import Path
from shutil import copy2, copytree
from hashlib import md5, sha256, file_digest


source_dir = Path(r'C:\Personal\Downloads\Python\screens')
target_dir = Path(Path.cwd() / 'target') # NOTE: may need to be changed later when packaged
print(source_dir, target_dir)

# get file metadata for comparison
def get_stats(filepath: Path) -> tuple:
    stats = filepath.stat()
    return stats.st_size, stats.st_mtime

def get_hash(filepath: Path | str) -> str:
    with open(filepath, 'rb') as file:
        checksum = file_digest(file, 'sha256').hexdigest()
    return checksum

source_testfile = Path(r'C:\Personal\Downloads\Python\py.png')
# print(get_hash(source_testfile))
# print(get_stats(source_testfile))


def compare(filepath: Path): # do I need go to this way - it's simple enough?
    print(f'Comparing {filepath}')


# walk target dir: check for superfluous items (deletions)
for root, dirs, files in target_dir.walk(top_down=False):
    for dir_ in dirs:
        sourcepath = source_dir / dir_
        if not Path.is_dir(sourcepath):
            print(f'Deleting dir {dir_}') # Path.rmdir()
    for file_ in files:
        sourcepath = source_dir / file_
        if not Path.is_file(sourcepath):
            print(f'Deleting {file_}') # Path.unlink(missing_ok=False)


# walk source dir
for root, dirs, files in source_dir.walk():
    for dir_ in dirs:
        targetpath = target_dir / dir_
        if not Path.is_dir(targetpath):
            print(f'Creating dir {dir_}') # shutil.copytree
    for file_ in files:
        #compare(root / file_) # pipeline start (1)
        targetpath = target_dir / file_
        if Path.is_file(targetpath):
            if get_stats(root / file_) != get_stats(targetpath):
                print(f'Replacing {file_}') # shutil.copy2
        else:
            print(f'Copying {file_}') # shutil.copy2







