#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import getpass
import logging
import argparse

from .cgroup import BASE_CGROUPS, CgroupsException

logger = logging.getLogger(__name__)


def create_user_cgroups(user):
    # Get user
    if user is None:
        user = getpass.getuser()
    logger.info('Creating cgroups sub-directories for user %s' % user)
    # Get hierarchies and create cgroups sub-directories
    try:
        hierarchies = os.listdir(BASE_CGROUPS)
    except OSError as e:
        if e.errno == 2:
            raise CgroupsException(
                "cgroups filesystem is not mounted on %s" % BASE_CGROUPS)
        else:
            raise OSError(e)
    logger.debug('Hierarchies available: %s' % hierarchies)
    for hierarchy in hierarchies:
        user_cgroup = os.path.join(BASE_CGROUPS, hierarchy, user)
        try:
            os.mkdir(user_cgroup)
        except OSError as e:
            if e.errno == 13:
                raise CgroupsException(
                    "Permission denied, you don't have root privileges")
            elif e.errno == 17:
                pass
            else:
                raise OSError(e)
    logger.warn('cgroups sub-directories created for user %s' % user)


def main():

    # Arguments
    parser = argparse.ArgumentParser(
        description='Allow a non-root user to use cgroups')
    parser.add_argument(
        '-v', '--verbose', required=False,
        default='INFO', help='Logging level (default "INFO")'
    )
    parser.add_argument(
        '-u', '--user', required=False,
        help='User to grant privileges to use cgroups'
    )
    args = parser.parse_args()

    # Logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logstream = logging.StreamHandler()
    logstream.setFormatter(formatter)
    logger.addHandler(logstream)
    if args.verbose == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 'INFO':
        logger.setLevel(logging.INFO)
    elif args.verbose == 'WARN':
        logger.setLevel(logging.WARN)
    else:
        logger.setLevel(logging.ERROR)
    logger.debug('Logging level: %s' % args.verbose)

    # Launch
    create_user_cgroups(args.user)


if __name__ == '__main__':
    main()
