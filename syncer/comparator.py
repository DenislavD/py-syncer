import sys
import logging
from pathlib import Path
from hashlib import md5, file_digest
from enum import StrEnum
from dataclasses import dataclass
from pprint import pprint

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# @TODO:
# determine_action(source_file, target_file) -> Action. (dry-run problem)
# file actions in try/except w/ logging

class Action(StrEnum):
    COPY = 'copy'
    DELETE = 'delete'

@dataclass
class Diff:
    source: str | None
    target: str | None
    Action: Action

class Comparator:
    def __str__(self):
        return 'Custom class that gets a source and target directory and yields Diff objects.'

    def __repr__(self):
        return f'Comparator with {len(self._source_set)=} and {len(self._target_set)=} items.'

    def __init__(self, source: Path, target: Path, strategy='stats'):
        self._source_dir = source
        self._target_dir = target
        self.strategy = strategy
        self._source_set = Comparator.get_filelist_in_dir(source)
        self._target_set = Comparator.get_filelist_in_dir(target)

    def __len__(self):
        return len(self._source_set)

    def run(self):
        deletions = self._target_set - self._source_set
        additions = self._source_set - self._target_set
        intersection = self._source_set & self._target_set

        for item in sorted(deletions, reverse=True): # need to delete folder contents first
            abspath = self._target_dir / item
            yield Diff(source=None, target=str(abspath), Action=Action.DELETE)

        for item in sorted(additions):
            if item.parent not in additions: # whole directory to be copied, skip sub-tree
                abspath_source = self._source_dir / item
                abspath_target = self._target_dir / item
                yield Diff(source=str(abspath_source), target=str(abspath_target), Action=Action.COPY)

        for item in sorted(intersection):
            abspath_source = self._source_dir / item
            abspath_target = self._target_dir / item
            if not self.compare_files(abspath_source, abspath_target): # shutil.copy replaces existing
                yield Diff(source=str(abspath_source), target=str(abspath_target), Action=Action.COPY)

    def compare_files(self, sourcefile, targetfile) -> bool:
        try:
            comparison_fn = getattr(Comparator, f'get_{self.strategy}')
        except AttributeError as exc:
            raise NotImplementedError(exc) from None
        else:
            return comparison_fn(sourcefile) == comparison_fn(targetfile)
    

    # get file metadata for comparison
    @staticmethod
    def get_stats(filepath: Path) -> tuple:
        stats = filepath.stat()
        return stats.st_size, stats.st_mtime

    @staticmethod
    def get_hash(filepath: Path | str) -> str:
        with open(filepath, 'rb') as file:
            checksum = file_digest(file, 'md5').hexdigest()
        return checksum

    @staticmethod
    def get_filelist_in_dir(mydir: Path) -> set:
        if not mydir.is_dir():
            log.error(f'{mydir} does not exist: please create it first. Exiting program.')
            sys.exit()
        
        filelist = { path.relative_to(mydir) for path in mydir.rglob('*') }
        if not filelist:
            log.warning(f'{mydir} is empty.')
        return filelist


# test data
# source = {WindowsPath('createdir'), WindowsPath('createdir/addfile_indir.txt'), WindowsPath('Screenshot 2025-11-11 183727.png'), 
# WindowsPath('Screenshot 2025-11-11 190933.png'), WindowsPath('Screenshot 2025-11-11 225208.png')}
# target = {WindowsPath('deldir'), WindowsPath('deldir/1'), WindowsPath('deldir/delfile_indir.txt'), 
# WindowsPath('Screenshot 2025-11-11 190933.png'), WindowsPath('Screenshot 2025-11-11 225208.png'), WindowsPath('yeah')} 
# c = Comparator(source, target)
# print(c)

def info():
    # walk target dir: check for superfluous items (deletions)
    # if not in source
    for root, dirs, files in target_dir.walk(top_down=False):
        for dir_ in dirs:
            sourcepath = source_dir / dir_
            if not Path.is_dir(sourcepath):
                log.info(f'Deleting dir {dir_}') # Path.rmdir()
        for file_ in files:
            sourcepath = source_dir / file_
            if not Path.is_file(sourcepath):
                log.info(f'Deleting {file_}') # Path.unlink(missing_ok=False)


    # walk source dir
    for root, dirs, files in source_dir.walk():
        for dir_ in dirs:
            targetpath = target_dir / dir_
            if not Path.is_dir(targetpath):
                log.info(f'Creating dir {dir_}') # shutil.copytree
        for file_ in files:
            #compare(root / file_) # pipeline start (1)
            targetpath = target_dir / file_
            if Path.is_file(targetpath):
                if get_stats(root / file_) != get_stats(targetpath):
                    log.info(f'Replacing {file_}') # shutil.copy2
            else:
                log.info(f'Copying {file_}') # shutil.copy2