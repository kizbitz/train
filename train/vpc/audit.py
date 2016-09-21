#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto.ec2
import boto.vpc

from boto.iam.connection import IAMConnection

from config import *

# TODO
# don't pass in conn????
# loop through regions for everything


def header(txt):
    print "*" * 30
    print txt
    print "*" * 30


def list_users():
    """List all user information"""

    header("AWS Users")
    conn = IAMConnection()
    users = conn.get_all_users()

    for user in users.list_users_result.users:
        print "- Username: {0}".format(user.user_name)
        print "    Created: {0}".format(user.create_date.split('T')[0])
        print "    User ID: {0}".format(user.user_id)
        try:
            print "    Password Last Used: {0}".format(user.password_last_used.split('T')[0])
        except:
            print "    Password Last Used: N/A"
    print ""


def get_regions():
    regions = boto.ec2.regions()

    final = []
    for r in regions:
        final.append(str(r).split(':')[1])

    # Remove isolated/special regions
    final.remove('cn-north-1') # China/Bejing
    final.remove('us-gov-west-1') #GovCloud

    final.sort()
    return final


def list_vpcs(conn):


    header("VCP Information")
    regions = get_regions()

    for r in regions:
        print "=" * (8 + len(r))
        print "Region: {0}".format(r)
        print "=" * (8 + len(r))
        print ""
        conn = boto.vpc.connect_to_region(r)
        vpcs = conn.get_all_vpcs()

        for v in vpcs:
            print "ID: {0}".format(v.id)
            print "~" * 16
            print "  Is Default: {0}".format(v.is_default)
            print "  State: {0}".format(v.state)
            print "  CIDR Block: {0}".format(v.cidr_block)
            if v.tags:
                print "  Tags:"
                for k,v in v.tags.iteritems():
                    print "    {0}: {1}".format(k, v)
            print ""
        print ""


def generate_report(conn):
    list_users()
    list_vpcs(conn)
