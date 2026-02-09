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

logging.getLogger('syncer').setLevel(logging.DEBUG)

from .scanner import Scanner, Strategy
from .handler import Client, HANDLER

log = logging.getLogger('syncer.main')

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
    parser.add_argument('--exclude', default='', type=str,
        help='Patterns to exclude from search. Example: .git|__pycache__|logs') # .git, __pycache__ ..
    # @TODO
    parser.add_argument('--workers', help='Use more CPU threads.')
    args = parser.parse_args()
    print(args)
    
    # normalize source and target directories
    source_dir = Path(args.source).absolute()
    if not source_dir.is_dir():
        log.error(f'{source_dir} must be a valid directory path.')
        raise SystemExit
    target_dir = Path(args.target).absolute()
    if not target_dir.is_dir():
        log.error(f'{target_dir} must be a valid directory path.')
        raise SystemExit
    log.info(f'{source_dir} -> {target_dir}')

    comparison_strategy = args.hash or Strategy.STATS
    scanner = Scanner(source_dir, target_dir, comparison_strategy, args.exclude)
    item_generator = scanner.run()
    
    client = Client.DRYRUN if args.dry_run else Client.FILESYSTEM
    handler_fn = HANDLER[client]
    handler_fn(item_generator, args.confirm, args.delete)



if __name__ == '__main__':
    main()

# initial development
# py main.py "C:\Personal\Downloads\Python\screens" target -d

# quick and dirty after packaged
# python -m syncer.main source target -d

# standard
# .\venvsyncer\Scripts\activate
# syncer "C:\Personal\Downloads\Python\screens" syncer\target -d
# syncer "C:\Personal\Downloads\Python\screens" syncer\target -d --exclude ".git|__pycache__|logs" -x -c
