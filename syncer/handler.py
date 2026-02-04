import logging
from enum import StrEnum
from shutil import copy2, copytree
import os
from typing import Callable

from .scanner import Action

log = logging.getLogger('syncer.handler')

class Client(StrEnum):
    DRYRUN = 'dry-run'
    FILESYSTEM = 'filesystem'

def execute_dryrun(gen, allow_replace, allow_delete):
    log.info('Starting Dry run..')
    for item in gen:
        if item.Action == Action.DELETE and allow_delete:
            if not os.access(item.target, os.W_OK):
                log.warning(f'No access rights for {item.target} , skipping item.')
                continue

            if item.target.is_dir():
                log.info(f'Deleting directory: {item.target}')
            else:
                log.info(f'Deleting file: {item.target}')
        elif item.Action == Action.REPLACE and allow_replace or item.Action == Action.COPY:
            if not os.access(item.source, os.R_OK): # doesn't work on Windows..
                log.warning(f'No access rights for {item.source} , skipping item.')
                continue
                
            if item.source.is_dir():
                log.info(f'Copying directory recursively: {item.source}')
            else:
                log.info(f'Copying file: {item.source}')


# Helper action functions
def node_delete(path) -> bool:
    try:
        if path.is_dir():
            log.info(f'> Deleting directory: {path}')
            path.rmdir()
        else:
            log.info(f'> Deleting file: {path}')
            path.unlink(missing_ok=False)
        return True
    except PermissionError:
        log.warning(f'No access rights for {path} , skipping item.')
        return False

def node_copy(sourcepath, targetpath) -> bool:
    try:
        if sourcepath.is_dir():
            log.info(f'> Copying directory recursively: {sourcepath}')
            copytree(sourcepath, targetpath, dirs_exist_ok=True)
        else:
            log.info(f'> Copying file: {sourcepath}')
            copy2(sourcepath, targetpath)
        return True
    except PermissionError:
        log.warning(f'No access rights for {sourcepath} , skipping item.')
        return False


def execute_filesystem(gen, allow_replace, allow_delete):
    log.info('Starting Synchronization process..')
    actions_cnt = 0
    for item in gen:
        if item.Action == Action.DELETE and allow_delete: # DELETES FILES !!
            if node_delete(item.target):
                actions_cnt += 1
        elif item.Action == Action.REPLACE and allow_replace: # DELETES FILES !!
            if item.source.is_dir() != item.target.is_dir():
                # remove target file/dir, copy-replace doesn't work with different obj types
                node_delete(item.target)
            if node_copy(item.source, item.target):
                actions_cnt += 1
        elif item.Action == Action.COPY and item.target.parent.is_dir():
            if node_copy(item.source, item.target):
                actions_cnt += 1
        
    log.info(f'Process completed with {actions_cnt} differring items handled.')


HANDLER: dict[Client, Callable] = {
    Client.DRYRUN: execute_dryrun,
    Client.FILESYSTEM: execute_filesystem,
}
