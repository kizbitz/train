#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os

from config import *
import instances as inst
import util


def _prompt_config(lab, path):
    """Prompt for the lab configuration script"""

    files = [f for f in os.listdir(path) if f.endswith('.py')]
    files.sort()

    if len(files) == 1:
        return {'1': files[0].strip('.py')},'1'
    else:
        print "Available configurations for the '{0}' lab:\n".format(lab)
        options = []
        for f in files:
            if f.endswith('.py'):
                options.append(f.strip('.py'))

        return util.list_prompt('\nWhich configuration would you like to execute?: ', options)


def list_available_labs():
    """List available labs in LAB_DIR"""

    available_labs = [d for d in os.listdir(LAB_DIR)
                      if os.path.isdir(os.path.join(LAB_DIR, d))]

    print "\nAvailable Labs:"

    available_labs.sort()
    for lab in available_labs:
        print '  {0}'.format(lab)

    print ''


def lab_description(lab):
    """Display information for a single lab"""

    file = open(LAB_DIR + lab + '/description.md', 'r')
    print '\n', file.read()
    file.close()


def calculate_lab_tag(conn, user_vpc, lab):
    """Auto-increment lab ID numbers"""

    labs = []
    instances = inst.get_vpc_instances(conn, user_vpc)

    # get all lab tags
    for instance in instances:
        if 'Lab' in instance.tags:
            if instance.tags['Lab'].startswith(lab):
                labs.append(instance.tags['Lab'])

    # remove duplicates
    labs = list(set(labs))

    # find first unused number
    count = 1
    while lab + '-' + str(count) in labs:
        count += 1

    return lab + '-' + str(count)


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
        print "\nRunning labs:"
        for lab in labs:
            print " ", lab
        print ""

        return labs
    else:
        print "\nNo labs running ...\n"


def lab_info(conn, user_vpc):
    """List all running labs in AWS"""

    labs = get_running_labs(conn, user_vpc)

    if labs:
        for lab in labs:
            print "Instances running in lab '{0}':".format(lab)
            instances = get_lab_instance_info(conn, user_vpc, lab)
            for instance in instances:
                print instance
            print ""


def get_user_instance_info(conn, user_vpc, lab_tag, user):
    """List IP/DNS for each instance for user"""

    reservations = conn.get_all_instances(filters = {'vpc-id': user_vpc.id,
                                                     'tag:Lab': lab_tag,
                                                     'tag:User': user})

    final = []
    for r in reservations:
        for instance in r.instances:
            final.append("""
Name:         {0}
  IP:         {1}
  Private IP: {2}
  Public DNS: {3}\n""".format(instance.tags['Name'],
                                instance.ip_address,
                                instance.private_ip_address,
                                instance.public_dns_name))
    final.sort()

    return final


def get_lab_instance_info(conn, user_vpc, lab_tag):
    """List instance info for lab"""

    reservations = conn.get_all_instances(filters = {'vpc-id': user_vpc.id,
                                                     'tag:Lab': lab_tag})

    final = []
    for r in reservations:
        for instance in r.instances:
            final.append("""
    Name:         {0}
      Lab:        {1}
      Region:     {2}
      IP:         {3}
      Private IP: {4}
      Public DNS: {5}""".format(instance.tags['Name'],
                                instance.tags['Lab'],
                                str(instance.region).replace('RegionInfo:',''),
                                instance.ip_address,
                                instance.private_ip_address,
                                instance.public_dns_name))
    final.sort()

    return final


def launch_lab(conn, user_vpc, lab):
    """Execute a lab configuration"""

    path = LAB_DIR + lab + '/scripts/'
    prompt, answer = _prompt_config(lab, path)

    # import lab configs
    labmod = imp.load_source('labmod', path + prompt[answer] + '.py')
    labmod.pre_process()
    cfg = util.read_config(LAB_DIR + lab + '/instances.cfg')

    # prompt for any dynamic configuration options
    for instance in cfg['instance']:
        for k, v in instance.iteritems():
            if str(v).startswith('PROMPT:'):
                instance[k] = raw_input('{0}: '.format(v.split(':')[1]))
            if str(v).startswith('PROMPT#:'):
                instance[k] = int(raw_input('{0}: '.format(v.split(':')[1])))
        for device in instance['device']:
            for k, v in device.iteritems():
                if str(v).startswith('PROMPT:'):
                    device[k] = raw_input('{0}: '.format(v.split(':')[1]))
                if str(v).startswith('PROMPT#:'):
                    device[k] = int(raw_input('{0}: '.format(v.split(':')[1])))

    # connection and required info
    security_groups = conn.get_all_security_groups(filters = {'vpc-id': user_vpc.id})
    subnets = conn.get_all_subnets(filters = {'vpc-id': user_vpc.id})

    # launch
    inst.launch_instances(conn, user_vpc, prompt[answer],
                          lab, labmod, cfg, security_groups, subnets)
    labmod.post_process()


def terminate_lab(conn, user_vpc, lab_tag):
    """Terminate a single lab and all instances"""
    instance_ids = []
    instances = inst.get_vpc_instances(conn, user_vpc)

    # get all lab instances
    for instance in instances:
        if 'Lab' in instance.tags:
            if instance.tags['Lab'] == lab_tag:
                instance_ids.append(instance.id)

    conn.terminate_instances(instance_ids=instance_ids)

    try:
        with open(USER_FILE) as users:
            for user in users:
                os.remove('/host/{0}/users/{1}/{2}.txt'.format(VPC, user.strip(), lab_tag))
    except:
        print "No user files removed..."

    print "\nTerminate request sent for all lab instances ..."
    print "Lab '{0}' has been deleted ...\n".format(lab_tag)
