#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import os.path
import time

import boto

from config import *
import amis
import labs
import vpc


def _create_tags(conn, instance, current, lab_tag, user, amibuild, amikey, script):
    """Create instance tags"""

    print "Creating instance tags for: {0}-{1}...".format(user, instance['NAME'])
    tags = {'Name': '{0}-{1}'.format(user, instance['NAME']),
            'Lab': '{0}'.format(lab_tag),
            'Trainer': '{0}'.format(TRAINER),
            'User': '{0}'.format(user),
            'AMI-Build': '{0}'.format(amibuild),
            'AMI-Key': '{0}'.format(amikey),
            'Script': '{0}'.format(script)}

    conn.create_tags(current.id, tags)


def _check_name_tag(conn, user_vpc, instance):
    """Check for existing name tag"""

    instances = get_vpc_instances(conn, user_vpc)

    for i in instances:
        if i.tags['Name'] == TRAINER + '-' + instance['NAME']:
            print "An instance with the name tag '{0}' already exists ...".format(instance['NAME'])
            instance['NAME'] = raw_input("Enter a different name: ")
            _check_name_tag(conn, user_vpc, instance)

    return instance


def _create_elastic_ips(conn, instance, current, user):
    """Create AWS elastic IP"""

    if instance['ELASTIC_IP']:
        print "Allocating elastic ip for: {0} ...".format(instance['NAME'])
        elastic_ip = conn.allocate_address(domain='vpc')
        conn.associate_address(instance_id=current.id,
        allocation_id=elastic_ip.allocation_id)
    else:
        print "Elastic ip not specified for: {0}-{1}. Skipping ...".format(user, instance['NAME'])


# TODO: leaving just in case we want to implement later
# dns
#def _create_dns(instance):

    #r_conn = boto.route53.connect_to_region(config['AWS_REGION'])
    #zone = r_conn.get_zone(config['HOSTED-ZONE'])
    ## create zone if it doesn't exist
    #if zone:
        #print "Hosted zone {0} exists ...".format(config['HOSTED-ZONE'])
    #else:
        #print "Hosted zone '{0}' not found. Creating it ...".format(config['HOSTED-ZONE'])
        #zone = r_conn.create_zone(config['HOSTED-ZONE'])

    #if zone.find_records(instance['NAME'], 'CNAME'):
        #print "DNS entrry {0} exists ... deleting it".format(instance['NAME'])
        #zone.delete_cname(instance['NAME'])

    #print "Creating DNS entry for: {0} ...".format(instance['NAME'])
    #zone.add_cname(instance['NAME'], current.public_dns_name, ttl=config['DEFAULT-TTL'])


def configure_devices(instance):
    """Configure block device map and device info text for USER_DATA"""

    # block devices
    dinfo = ""
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    for device in instance['device']:
        block_device = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
        block_device.size = device['SIZE']
        block_device.delete_on_termination = device['DELETE_ON_TERMINATE']
        bdm[device['DEVICE']] = block_device

        # device info
        if device['MOUNT'] != "/":
            f = device['FILESYSTEM']
            m = device['MOUNT']
            d = device['DEVICE'].replace('s', 'xv')
            dinfo = "# device info"
            dinfo += '\nmkfs -t {0} {1}'.format(f, d)
            dinfo += '\nmkdir {0}'.format(m)
            dinfo += '\nmount {0} {1}'.format(d, m)
            dinfo += '\necho "{0} {1} {2} defaults 0 2" >> /etc/fstab'.format(d, m, f)

    return bdm, dinfo


def output_user_files(conn, user_vpc, lab_tag):
    """Write user lab/instance info file"""

    with open(USER_FILE) as users:
        for user in users:
            user = user.split(',')[0].strip()

            # directory to store instance info on host
            if not os.path.exists('/host/{0}/users/{1}'.format(VPC, user)):
                os.makedirs('/host/{0}/users/{1}'.format(VPC, user))

            info = labs.get_user_instance_info(conn, user_vpc, lab_tag, user)

            with open('/host/{0}/users/{1}/{2}.txt'.format(VPC, user, lab_tag), 'w') as f:
                f.write('AWS Instances:\n')
                for i in info:
                    f.write(i)


def get_vpc_instances(conn, vpc):
    """Get all vpc instances"""

    instances = []
    reservations = conn.get_all_reservations(filters = {'vpc-id': vpc.id})

    for r in reservations:
        instances.append(r.instances[0])

    return instances


def terminate_all_instances(conn, user_vpc):
    instance_ids = []
    instances = get_vpc_instances(conn, user_vpc)

    # get all ids
    for instance in instances:
        instance_ids.append(instance.id)

    if instance_ids:
        conn.terminate_instances(instance_ids=instance_ids)
        print "\nTerminate request sent for all instances ...\n"

        # remove all local user lab/instance details text files
        with open('/host/{0}/key-pairs.txt'.format(VPC)) as users:
            for user in users:
                for f in glob.glob('/host/{0}/users/{1}/*.txt'.format(VPC, user.split('-')[0])):
                    os.remove(f)

        return instances
    else:
        print "\nVPC has no instances ..."


def confirm_terminated(instances):
    """Check instance.state of instances to confirm termination"""

    for instance in instances:
        while instance.state != 'terminated':
            print "  Waiting for all instances to terminate ..."
            time.sleep(5)
            instance.update()


def launch_instances(conn, user_vpc, script, lab,
                     labmod, cfg, security_groups, subnets):
    """Launch lab instances for each user"""

    instances = []
    lab_tag = labs.calculate_lab_tag(conn, user_vpc, lab)
    print "Launching '{0}' lab with tag: {1}".format(lab, lab_tag)

    # debug log directory
    if not os.path.exists('train/logs'):
        os.makedirs('train/logs')

    zone_count = vpc.get_starting_zone(subnets)
    zone_max = zone_count + len(subnets)
    with open(USER_FILE) as users:
        for user in users:
            user = user.split(',')[0].strip()
            amikey = 0
            for instance in cfg['instance']:
                amibuild = True
                for count in range(instance['COUNT']):
                    current = instance.copy()
                    if 'NAME' in instance:
                        if current['COUNT'] > 1:
                            current['NAME'] = instance['NAME'] + '-' + str(count)
                        else:
                            current['NAME'] = instance['NAME']
                    if 'NAMES' in instance:
                        current['NAME'] = instance['NAMES'][count]

                    # autorotate zones
                    if instance['COUNT'] > 1:
                        current['ZONE'] = zone_count
                        zone_count += 1
                        if zone_count == zone_max:
                            zone_count = vpc.get_starting_zone(subnets)

                    # check for unique 'Name' tag
                    # Removed this check for speed
                    # TODO: Handle somehow - prompt or autoset a name
                    #_check_name_tag(conn, user_vpc, current)

                    # security group ids
                    sids = vpc.get_sg_ids(cfg, current, security_groups, VPC_TAG)

                    # device info
                    bdm, dinfo = configure_devices(current)

                    # network interface
                    interface = vpc.create_interface(vpc.get_subnet_id(current, subnets), sids)

                    # ami id
                    ami_id = AMIS[getattr(labmod, current['AMI_KEY'])]

                    # custom ami available?
                    images = conn.get_all_images(owners = ['self'])
                    name_tag = TRAINER + '-{0}-'.format(VPC) + \
                                         '{0}-'.format(lab) + \
                                         '{0}-'.format(script) + \
                                         '{0}'.format(amikey)
                    for image in images:
                        if 'Lab' in image.tags:
                            if image.tags['Name'] == name_tag:
                                current['SCRIPT'] = 'AMIBUILD'
                                ami_id = image.id

                    # user data script
                    udata = getattr(labmod, current['SCRIPT'])

                    # save the 'user data' script for reference
                    # useful for lab creation/debug
                    with open('train/logs/{0}.sh'.format(current['NAME']), 'w') as file:
                        file.write(udata.format(fqdn=current['NAME'], dinfo=dinfo))

                    # launch instance
                    print "Launching instance: {0}-{1} ...".format(user, current['NAME'])
                    reservation = conn.run_instances(image_id=ami_id,
                                                     key_name=user + '-{0}'.format(VPC),
                                                     user_data=udata.format(fqdn=current['NAME'],
                                                                            dinfo=dinfo),
                                                     instance_type=current['INSTANCE_TYPE'],
                                                     network_interfaces=interface,
                                                     block_device_map = bdm,
                                                     instance_profile_name=VPC_TAG)

                    # get instance object
                    current_res = reservation.instances[0]

                    # save instance/current
                    instances.append([current, current_res, user, amibuild, amikey, script])
                    amibuild = False

                amikey += 1

    # wait for all instances to finish booting
    print "Waiting for instances to initialize ..."
    time.sleep(20)
    for instance in instances:
        while instance[1].state != 'running':
            print "Waiting for instance '{0}-{1}' to initialize ...".format(instance[2],
                                                                              instance[0]['NAME'])
            time.sleep(0.5)
            instance[1].update()

    # set elastic ips and tag instances
    for instance in instances:
        # disable elastic_ips (for now)
        #_create_elastic_ips(conn, instance[0], instance[1], instance[2])
        _create_tags(conn, instance[0], instance[1], lab_tag,
                      instance[2], instance[3], instance[4], instance[5])

    final = labs.get_lab_instance_info(conn, user_vpc, lab_tag)
    output_user_files(conn, user_vpc, lab_tag)

    print "\nLab '{0}' launched with tag '{1}':".format(lab, lab_tag)
    print "\n  Instances:"
    for instance in final:
        print instance
    print ''
