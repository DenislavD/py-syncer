import sys
import logging
from pathlib import Path
from hashlib import sha1, md5, file_digest
from enum import StrEnum
from dataclasses import dataclass
from pprint import pprint

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# @TODO:
# file actions in try/except w/ logging

class Strategy(StrEnum):
    STATS = 'stats'
    HASH = 'hash'

class Action(StrEnum):
    COPY = 'copy'
    DELETE = 'delete'

@dataclass
class Diff:
    source: str | None
    target: str | None
    Action: Action

class Scanner:
    def __str__(self):
        return 'Custom class that gets a source and target directory and yields Diff objects.'

    def __repr__(self):
        return f'Scanner with {len(self.source_set)=} and {len(self.target_set)=} items.'

    def __init__(self, source: Path, target: Path, strategy=Strategy.STATS):
        self.source_dir = source
        self.target_dir = target
        self.source_set = Scanner.get_filelist_in_dir(source)
        self.target_set = Scanner.get_filelist_in_dir(target)
        strategy_map = {
            Strategy.STATS: Scanner.get_stats,
            Strategy.HASH: Scanner.get_hash,
        }
        self.comparison_fn = strategy_map[strategy]

    def __len__(self):
        return len(self.source_set)

    def run(self):
        deletions = self.target_set - self.source_set
        additions = self.source_set - self.target_set
        intersection = self.source_set & self.target_set

        for item in sorted(deletions, reverse=True): # need to delete folder contents first
            abspath = self.target_dir / item
            yield Diff(source=None, target=str(abspath), Action=Action.DELETE)

        for item in sorted(additions):
            if item.parent not in additions: # whole directory to be copied, skip sub-tree
                abspath_source = self.source_dir / item
                abspath_target = self.target_dir / item
                yield Diff(source=str(abspath_source), target=str(abspath_target), Action=Action.COPY)

        for item in sorted(intersection):
            abspath_source = self.source_dir / item
            abspath_target = self.target_dir / item
            if abspath_source.is_file() or abspath_target.is_file():
                if not self.compare_files(abspath_source, abspath_target): # shutil.copy replaces existing
                    yield Diff(source=str(abspath_source), target=str(abspath_target), Action=Action.COPY)

    def compare_files(self, sourcefile, targetfile) -> bool:
        try:
            return self.comparison_fn(sourcefile) == self.comparison_fn(targetfile)
        except AttributeError as exc:
            raise NotImplementedError(exc) from None
    

    # get file metadata for comparison
    @staticmethod
    def get_stats(filepath: Path) -> tuple:
        stats = filepath.stat()
        return stats.st_size, stats.st_mtime

    @staticmethod
    def get_hash(filepath: Path | str, algo: str='md5') -> str:
        with open(filepath, 'rb') as file:
            checksum = file_digest(file, algo).hexdigest()
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
# c = Scanner(source, target)
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