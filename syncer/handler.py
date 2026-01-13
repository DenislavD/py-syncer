import logging
from enum import StrEnum
from shutil import copy2, copytree
from typing import Callable

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Client(StrEnum):
    DRYRUN = 'dry-run'
    FILESYSTEM = 'filesystem'

def execute_dryrun(gen):
    log.info('Starting Dry run..')


def execute_filesystem(gen):
    log.info('Starting Synchronization process..')


HANDLER: dict[Client, Callable] = {
    Client.DRYRUN: execute_dryrun,
    Client.FILESYSTEM: execute_filesystem,
}








# print('I am here.')
# print(CLIENT_MAP[Client.DRYRUN](range(3)))