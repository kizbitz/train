#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Train: AWS CLI Tool"""

import argparse
import sys

import boto.vpc

from vpc.config import *
import vpc.instances as inst
import vpc.labs as labs
import vpc.util as util
import vpc.vpc as vpc


# configure parser
parser = argparse.ArgumentParser(description='Train: AWS CLI Tool')
parser.add_argument('-k',
                    help='Create AWS key pairs',
                    action='store_true', required=False)

parser.add_argument('-v',
                    help='Create AWS VPC',
                    action='store_true', required=False)

parser.add_argument('-a',
                    help='List all available labs',
                    action='store_true', required=False)

parser.add_argument('-i', metavar='<lab>',
                    help='View description for an available lab',
                    required=False)

parser.add_argument('-x', metavar='<lab>',
                    help='Excecute a lab',
                    required=False)

parser.add_argument('-l',
                    help='List running labs and instances in AWS',
                    action='store_true', required=False)

parser.add_argument('-d', metavar='<tag>',
                    help='Delete a lab from AWS',
                    required=False)

parser.add_argument('-p',
                    help='Purge/Delete all instances in vpc',
                    action='store_true', required=False)

parser.add_argument('-t', 
                    help='Terminate environment (VPC and local files)',
                    action='store_true', required=False)

args = parser.parse_args()


def process():
    """Execute command/flags"""

    if args.k:
        vpc.create_key_pairs()
    if args.v:
        print "Creating AWS VPC ..."
        vpc.create_vpc()
    if args.a:
        labs.list_available_labs()
    if args.i:
        labs.lab_description(args.i)

    # vpc and connection required for the following options...
    conn = boto.vpc.connect_to_region(AWS_REGION)
    user_vpc = vpc.get_vpc_id(conn, TRAINER + '-{0}'.format(TRAIN_TAG))
    if not user_vpc:
        print "\n'{0}' VPC doesn't exist.".format(TRAINER + '-{0}'.format(TRAIN_TAG))
        print "Create it by running the command: train -v\n"
        sys.exit(1)

    if args.x:
        labs.launch_lab(conn, user_vpc, args.x)
    if args.l:
        labs.lab_info(conn, user_vpc)
    if args.d:
        labs.terminate_lab(conn, user_vpc, args.d)
    if args.p:
        inst.terminate_all_instances(conn, user_vpc)
    if args.t:
        vpc.terminate_environment(conn, user_vpc)


if __name__ == '__main__':
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    process()
