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

def execute_dryrun(gen, allow_replace, allow_delete):
    log.info('Starting Dry run..')
    for item in gen:
        if item.Action == Action.DELETE and allow_delete:
            if item.target.is_dir():
                log.info(f'Deleting directory: {item.target}')
            else:
                log.info(f'Deleting file: {item.target}')
        elif item.Action == Action.REPLACE and allow_replace or item.Action == Action.COPY:
            if item.source.is_dir():
                log.info(f'Copying directory recursively: {item.source}')
            else:
                log.info(f'Copying file: {item.source}')            


# Helper action functions
def node_delete(path):
    if path.is_dir():
        log.info(f'> Deleting directory: {path}')
        path.rmdir()
    else:
        log.info(f'> Deleting file: {path}')
        path.unlink(missing_ok=False)

def node_copy(sourcepath, targetpath):
    if sourcepath.is_dir():
        log.info(f'> Copying directory recursively: {sourcepath}')
        copytree(sourcepath, targetpath, dirs_exist_ok=True)
    else:
        log.info(f'> Copying file: {sourcepath}')
        copy2(sourcepath, targetpath)


def execute_filesystem(gen, allow_replace, allow_delete):
    log.info('Starting Synchronization process..')
    count = 0
    for item in gen:
        if item.Action == Action.DELETE and allow_delete: # DELETES FILES !!
            node_delete(item.target)
            count += 1
        elif item.Action == Action.REPLACE and allow_replace: # DELETES FILES !!
            if item.source.is_dir() != item.target.is_dir():
                # remove target file/dir, copy-replace doesn't work with different obj types
                node_delete(item.target)
            node_copy(item.source, item.target)
            count += 1
        elif item.Action == Action.COPY and item.target.parent.is_dir():
            node_copy(item.source, item.target)
            count += 1
        
    log.info(f'Process completed with {count} differring items handled.')


HANDLER: dict[Client, Callable] = {
    Client.DRYRUN: execute_dryrun,
    Client.FILESYSTEM: execute_filesystem,
}
