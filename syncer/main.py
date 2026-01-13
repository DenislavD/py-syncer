import sys
from pathlib import Path
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

from scanner import Scanner, Strategy
from handler import Client, HANDLER


def main():
    # argparse
    
    source_dir = Path(r'C:\Personal\Downloads\Python\screens')
    target_dir = Path(Path.cwd() / 'target') # NOTE: may need to be changed later when packaged
    log.info(f'{source_dir} -> {target_dir}')

    scanner = Scanner(source_dir, target_dir, Strategy.STATS)
    diff_obj_gen = scanner.run()
    # for item in diff_obj_gen:
    #     print(item.Action, item.source, item.target)
    # call handler
    myclient = Client.DRYRUN # FILESYSTEM
    handler_fn = HANDLER[myclient]
    handler_fn(diff_obj_gen)



if __name__ == '__main__':
    main()



