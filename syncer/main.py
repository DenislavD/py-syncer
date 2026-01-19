import sys
from pathlib import Path
import argparse
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

from scanner import Scanner, Strategy
from handler import Client, HANDLER


def main():
    # argparse
    parser = argparse.ArgumentParser(prog='Incremental File Syncer', description='Syncs a source directory to a target.')
    parser.add_argument('source')
    parser.add_argument('target')
    parser.add_argument('-d', '--dry-run', action='store_true', help='List actions as log items only.')
    parser.add_argument('-c', '--confirm', action='store_true', help='Confirm replacing files.')
    parser.add_argument('-x', '--delete', action='store_true', help='Confirm deleting extra files in target.')
    parser.add_argument('--hash', action='store_const', const=Strategy.HASH,
        help='Use hash to compare files instead of metadata.')
    # @TODO
    parser.add_argument('--workers', help='Use more CPU threads.')
    parser.add_argument('--exclude', help='Patterns to exclude from search. Example: .git|__pycache__|logs') # .git, __pycache__ ..
    args = parser.parse_args()
    print(args)
    
    source_dir = Path(r'C:\Personal\Downloads\Python\screens')
    target_dir = Path(Path.cwd() / 'target') # NOTE: may need to be changed later when packaged
    log.info(f'{source_dir} -> {target_dir}')

    comparison_strategy = args.hash or Strategy.STATS
    scanner = Scanner(source_dir, target_dir, comparison_strategy)
    item_generator = scanner.run()
    
    client = Client.FILESYSTEM # DRYRUN or FILESYSTEM
    handler_fn = HANDLER[client]
    handler_fn(item_generator)



if __name__ == '__main__':
    main()



