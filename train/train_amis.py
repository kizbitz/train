#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Train-AMIS: AWS CLI AMI Managment"""

import argparse
import sys

import boto

from vpc.config import *
import vpc.labs as labs
import vpc.amis as amis

conn = boto.connect_iam(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# configure parser
parser = argparse.ArgumentParser(description='Train: AWS CLI AMI Management')

parser.add_argument('-a',
                    help='List all available labs',
                    action='store_true', required=False)

parser.add_argument('-c', metavar='<lab>',
                    help="Create lab AMI's",
                    required=False)

parser.add_argument('-d', metavar='<lab>',
                    help="Delete lab AMI's",
                    required=False)

parser.add_argument('-l',
                    help="List all AMI's",
                    action='store_true', required=False)

args = parser.parse_args()


def process():
    """Execute command/flags"""

    if args.a:
        labs.list_available_labs()
    if args.c:
        amis.create_amis(conn, args.c)
    if args.d:
        amis.delete_amis(conn, args.d)
    if args.l:
        amis.list_amis(conn)


if __name__ == '__main__':
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    process()
