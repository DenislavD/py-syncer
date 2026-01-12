import sys
import os.path
from pathlib import Path, PurePath
from shutil import copy2, copytree
from enum import StrEnum
from pprint import pprint
import logging

logging.basicConfig( # root level, valid for all imports as well
    handlers = [
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(Path(__file__).parent / 'logs' / 'logfile.log')
    ],
    level=logging.WARNING,
    format='%(asctime)s: %(levelname)s@%(filename)s~%(lineno)d: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from comparator import Comparator

class Strategy(StrEnum):
    STATS = 'stats'
    HASH = 'hash'

def main():
    # argparse
    
    source_dir = Path(r'C:\Personal\Downloads\Python\screens')
    target_dir = Path(Path.cwd() / 'target') # NOTE: may need to be changed later when packaged
    log.info(f'{source_dir} -> {target_dir}')

    comparator = Comparator(source_dir, target_dir, Strategy.STATS)
    for item in comparator.run():
        print(item.Action, item.source, item.target)




if __name__ == '__main__':
    main()



