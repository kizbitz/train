#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Train AMI image management"""

from config import *

import boto.vpc
import instances as inst
import labs as labs
import util


def get_running_labs(conn, user_vpc):
    """List/Return all running labs"""

    labs = []
    instances = inst.get_vpc_instances(conn, user_vpc)

    # get all lab tags
    for instance in instances:
        if 'Lab' in instance.tags:
            labs.append(instance.tags['Lab'])

    # remove duplicates
    labs = list(set(labs))

    labs.sort()

    if labs:
        return labs
    else:
        print "\nNo labs running ...\n"


def create_amis(conn, user_vpc, lab_tag):
    """Create all images for lab"""

    running_labs = get_running_labs(conn, user_vpc)

    cfg = util.read_config(LAB_DIR + lab_tag.rsplit('-', 1)[0] + '/instances.cfg')
    instances = inst.get_vpc_instances(conn, user_vpc)

    lab_instances = []
    for instance in instances:
        if 'Lab' in instance.tags:
            if instance.tags['Lab'] == lab_tag and instance.tags['AMI-Build'] == 'True':
                lab_instances.append(instance)


    print "Creating AMI's for lab: {0}".format(lab_tag)
    for instance in lab_instances:
        name_tag = TRAINER + '-{0}-'.format(TRAIN_TAG) + \
                             '{0}-'.format(lab_tag.rsplit('-', 1)[0]) + \
                             '{0}-'.format(instance.tags['Script']) + \
                             '{0}'.format(instance.tags['AMI-Key'])

        ami = conn.create_image(instance.id, name_tag, '{0} lab AMI'.format(lab_tag.rsplit('-', 1)[0]))

        # tags
        tags = {'Name': '{0}'.format(name_tag),
                'AMI-Key': '{0}'.format(instance.tags['AMI-Key']),
                'Lab': '{0}'.format(lab_tag.rsplit('-', 1)[0])}

        conn.create_tags(ami, tags)

    print "Completed ..."


def delete_amis(conn, lab_tag):
    """Delete all images for lab"""

    images = conn.get_all_images(owners = ['self'])

    tag = TRAINER + '-{0}-'.format(TRAIN_TAG) + '{0}-'.format(lab_tag)

    for image in images:
        if image.name.startswith(tag):
            print 'Degristering {0} ...'.format(image.name)
            conn.deregister_image(image.id, delete_snapshot=True)

    print "Completed ..."


def list_amis(conn):
    """List all AMI's in region"""

    images = conn.get_all_images(owners = ['self'])

    print "\nAWS AMI's:\n"
    for image in images:
        print '  ID: {0}'.format(image.id)
        print '  Name: {0}'.format(image.name)
        print '  Description: {0}'.format(image.description)
        print '  Region: {0}'.format(str(image.region).split(':')[1])
        print '  Tags:'
        for k,v in image.tags.iteritems():
            print '     {0}: {1}'.format(k,v)
        print ''

