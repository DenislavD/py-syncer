import sys
import logging
from pathlib import Path
from hashlib import sha1, md5, file_digest
from enum import StrEnum
from dataclasses import dataclass
from pprint import pprint

log = logging.getLogger('syncer.scanner')

class Strategy(StrEnum):
    STATS = 'stats'
    HASH = 'hash'

class Action(StrEnum):
    COPY = 'copy'
    REPLACE = 'replace'
    DELETE = 'delete'

@dataclass
class Diff:
    source: Path | None
    target: Path | None
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
            yield Diff(source=None, target=abspath, Action=Action.DELETE)

        for item in sorted(intersection):
            abspath_source = self.source_dir / item
            abspath_target = self.target_dir / item
            if abspath_source.is_file() or abspath_target.is_file():
                if not self.compare_files(abspath_source, abspath_target):
                    yield Diff(source=abspath_source, target=abspath_target, Action=Action.REPLACE)

        for item in sorted(additions):
            if item.parent not in additions: # whole directory to be copied, skip sub-tree
                abspath_source = self.source_dir / item
                abspath_target = self.target_dir / item
                yield Diff(source=abspath_source, target=abspath_target, Action=Action.COPY)

    def compare_files(self, sourcefile, targetfile) -> bool:
        try:
            return self.comparison_fn(sourcefile) == self.comparison_fn(targetfile)
        except AttributeError as exc:
            raise NotImplementedError(exc) from None
        except PermissionError:
            return True # skip files


    # get file metadata for comparison
    @staticmethod
    def get_stats(filepath: Path) -> tuple:
        stats = filepath.stat()
        return stats.st_size, stats.st_mtime

    @staticmethod
    def get_hash(filepath: Path, algo: str='md5') -> str:
        if filepath.is_dir(): return False
        
        try:
            with open(filepath, 'rb') as file:
                checksum = file_digest(file, algo).hexdigest()
        except PermissionError as e:
            log.warning(f'No access rights for {filepath}, skipping file.')
            raise PermissionError
        
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
