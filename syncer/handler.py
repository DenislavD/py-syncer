import logging
from enum import StrEnum
from shutil import copy2, copytree
from typing import Callable
from pprint import pprint

from scanner import Action

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Client(StrEnum):
    DRYRUN = 'dry-run'
    FILESYSTEM = 'filesystem'

def execute_dryrun(gen):
    log.info('Starting Dry run..')
    for item in gen:
        if item.Action == Action.DELETE and True:
            if item.target.is_dir():
                log.info(f'Deleting directory: {item.target}')
            else:
                log.info(f'Deleting file: {item.target}')
        else:
            if item.source.is_dir():
                log.info(f'Copying directory recursively: {item.source}')
            else:
                log.info(f'Copying file: {item.source}')            


def execute_filesystem(gen):
    log.info('Starting Synchronization process..')
    count = 0
    for item in gen:
        if item.Action == Action.DELETE and True: # DELETES FILES !!
            if item.target.is_dir():
                log.info(f'Deleting directory: {item.target}')
                item.target.rmdir()
            else:
                log.info(f'Deleting file: {item.target}')
                item.target.unlink(missing_ok=False)
            count += 1

        elif item.Action == Action.REPLACE: # DELETES FILES !!
            log.info(f'Replacing file: {item.target}')
            # remove old folder/file
            if item.target.is_dir():
                item.target.rmdir()
            else:
                item.target.unlink(missing_ok=False)
            # now copy cleanly - @TODO needs refactoring ~ delete_node, copy_node
            if item.source.is_dir():
                log.info(f'Copying directory recursively: {item.source}')
                copytree(item.source, item.target, dirs_exist_ok=True)
            else:
                log.info(f'Copying file: {item.source}')
                copy2(item.source, item.target)
            count += 1

        elif item.Action == Action.COPY:
            if item.source.is_dir():
                log.info(f'Copying directory recursively: {item.source}')
                copytree(item.source, item.target, dirs_exist_ok=True)
            else:
                log.info(f'Copying file: {item.source}')
                copy2(item.source, item.target)
            count += 1
    log.info(f'Process completed with {count} differring items handled.')


HANDLER: dict[Client, Callable] = {
    Client.DRYRUN: execute_dryrun,
    Client.FILESYSTEM: execute_filesystem,
}







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