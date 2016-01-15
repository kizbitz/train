#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Train-AMIS: AWS CLI AMI Managment"""

import argparse
import sys

import boto.ec2
import boto.vpc

from vpc.config import *
import vpc.images as images
import vpc.instances as inst
import vpc.labs as labs
import vpc.vpc as vpc


econn = boto.ec2.connect_to_region(AWS_REGION)
vconn = boto.vpc.connect_to_region(AWS_REGION)
user_vpc = vpc.get_vpc_id(vconn, TRAINER + '-{0}'.format(VPC))

# configure parser
parser = argparse.ArgumentParser(description='Train: AWS CLI AMI Management')

parser.add_argument('-c', metavar='<lab>',
                    help="Create lab AMI's",
                    required=False)

parser.add_argument('-d', metavar='<lab>',
                    help="Deregister lab AMI's",
                    required=False)

parser.add_argument('-l',
                    help="List all AMI's",
                    action='store_true', required=False)

parser.add_argument('-r',
                    help="List running labs",
                    action='store_true', required=False)

args = parser.parse_args()


def process():
    """Execute command/flags"""

    if args.c:
        images.create_amis(vconn, user_vpc, args.c)
    if args.d:
        images.delete_amis(econn, args.d)
    if args.l:
        images.list_amis(econn)
    if args.r:
        labs.get_running_labs(vconn, user_vpc)


if __name__ == '__main__':
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    process()
