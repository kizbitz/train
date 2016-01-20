#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import os
import shutil

import boto
import boto.ec2
from boto.ec2.connection import EC2Connection

from config import *
import instances as inst
import util


def _connect():
    """Return connection to AWS"""

    return boto.vpc.connect_to_region(AWS_REGION)



def _create_vpc(conn):
    """Create VPC in AWS"""

    print 'Creating VPC: {0} ...'.format(VPC_TAG)

    vpc = conn.create_vpc(VPC_CIDR)
    conn.modify_vpc_attribute(vpc.id, enable_dns_support=True)
    conn.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
    vpc.add_tag('Name', VPC_TAG)

    return vpc


def delete_vpc(user_vpc):
    """Delete AWS VPC"""

    print "Deleting VPC: {0} ...".format(TRAINER + '-{0}'.format(VPC))
    conn = boto.vpc.connect_to_region(AWS_REGION)

    subnets = conn.get_all_subnets(filters = {'vpc-id': user_vpc.id})
    igws = conn.get_all_internet_gateways(filters={'attachment.vpc-id': user_vpc.id})

    if subnets:
        for subnet in subnets:
            conn.delete_subnet(subnet.id)
    if igws:
        for igw in igws:
            conn.detach_internet_gateway(igw.id, user_vpc.id)
            conn.delete_internet_gateway(igw.id)

    conn.delete_vpc(user_vpc.id)


def _create_gateway(conn, vpc):
    """Create AWS IGW"""

    print 'Creating gateway: {0} ...'.format(IGW)

    gateway = conn.create_internet_gateway()
    gateway.add_tag('Name', IGW)
    conn.attach_internet_gateway(gateway.id, vpc.id)

    return gateway


def _create_route_table(conn, vpc, gateway):
    """Create AWS route table"""

    print 'Creating route table: {0} ...'.format(ROUTE_TABLE)

    route_table = conn.get_all_route_tables(filters = {'vpc-id':vpc.id})
    route = conn.create_route(route_table[0].id, '0.0.0.0/0', gateway.id)
    route_table[0].add_tag('Name', ROUTE_TABLE)

    return route_table


def _create_subnets(conn, vpc, route_table):
    """Create AWS subnets"""

    regions = [r.name for r in boto.ec2.regions()]
    zones = [z.name for z in conn.get_all_zones()]

    current_ip = 0
    for zone in zones:
        tag = TRAINER + '-{0}-'.format(VPC) + zone
        print "10.0.{0}.0/20".format(current_ip)

        print 'Creating subnet: {0} ...'.format(tag)
        subnet = conn.create_subnet(vpc.id,
                                    "10.0.{0}.0/20".format(current_ip),
                                    availability_zone=zone)
        subnet.add_tag('Name', tag)

        # associate route table
        conn.associate_route_table(route_table[0].id, subnet.id)

        # enable public IP's by default for the subnet
        # Note: this is a hack for now until boto is updated
        #  See: https://github.com/boto/boto/issues/2646
        #  and: https://github.com/boto/boto/pull/2678
        commands.getstatusoutput(
            'aws ec2 modify-subnet-attribute --subnet-id {0} --map-public-ip-on-launch'
            .format(subnet.id))

        current_ip += 16


def _configure_network_acl(conn, vpc):
    """Configure AWS ACL"""

    print 'Configuring network ACL: {0} ...'.format(NETWORK_ACL)
    acl = conn.get_all_network_acls(filters = {'vpc-id':vpc.id})
    acl[0].add_tag('Name', NETWORK_ACL)


def _configure_default_security_group(conn, vpc):
    """Configure AWS default security group"""

    print "Configuring default security group ..."
    default_sg_name = VPC_TAG + '-default'

    # since we just created the vpc, there is only the default security group
    sg = conn.get_all_security_groups(filters = {'vpc-id':vpc.id})

    # add the name tag
    sg[0].add_tag('Name', default_sg_name)

    # ensure no rules exist
    for rule in sg[0].rules:
        for grant in rule.grants:
            conn.revoke_security_group(group_id=sg[0].id,
                                       ip_protocol=rule.ip_protocol,
                                       from_port=rule.from_port,
                                       to_port=rule.to_port,
                                       src_security_group_group_id=grant.group_id,
                                       cidr_ip=grant.cidr_ip)

    for rule in sg[0].rules_egress:
        for grant in rule.grants:
            conn.revoke_security_group_egress(sg[0].id,
                                              rule.ip_protocol,
                                              rule.from_port,
                                              rule.to_port,
                                              grant.group_id,
                                              grant.cidr_ip)

    print 'Adding default egress rules ...'
    conn.authorize_security_group_egress(group_id=sg[0].id,
                                         ip_protocol="-1",
                                         from_port='-1',
                                         to_port='-1',
                                         cidr_ip='0.0.0.0/0')

    # allow traffic for vpc instances
    sg[0].authorize(ip_protocol="-1", src_group=sg[0])

    # add local IP
    #local_ip = commands.getstatusoutput('curl -s icanhazip.com')[1]
    #print 'Adding your current location IP ({0}) to default security group ...'.format(local_ip)
    #sg[0].authorize(ip_protocol='tcp',
                    #from_port='0',
                    #to_port='65535',
                    #cidr_ip=local_ip + '/32')

    # common
    sg[0].authorize(ip_protocol='tcp',
                    from_port='22',
                    to_port='22',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='80',
                    to_port='80',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='443',
                    to_port='443',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='2375',
                    to_port='2376',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='3375',
                    to_port='3376',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='5000',
                    to_port='5000',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='8000',
                    to_port='8000',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='8080',
                    to_port='8080',
                    cidr_ip='0.0.0.0/0')

    sg[0].authorize(ip_protocol='tcp',
                    from_port='9999',
                    to_port='9999',
                    cidr_ip='0.0.0.0/0')

def create_interface(subnet_id, sids):
    """Creates AWS EC2 network interface"""

    i = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=subnet_id,
                                                                groups=sids,
                                                                associate_public_ip_address=True)

    return boto.ec2.networkinterface.NetworkInterfaceCollection(i)


def create_iam_profile():
    """Creates AWS IAM profile"""

    print 'Creating IAM Profile: {0} ...'.format(IAM_PROFILE)

    conn = boto.connect_iam()
    instance_profile = conn.create_instance_profile(IAM_PROFILE)
    role = conn.create_role(TRAINER + '-{0}'.format(VPC))
    conn.add_role_to_instance_profile(IAM_PROFILE, IAM_PROFILE)
    conn.put_role_policy(IAM_PROFILE, 'EC2-Describe', POLICY)

    print 'IAM profile, role, and policy created ...'


def delete_iam_profile():
    """Delete AWS IAM profile"""

    print 'Deleting IAM Profile: {0} ...'.format(IAM_PROFILE)

    conn = boto.connect_iam()
    conn.delete_role_policy(IAM_PROFILE, 'EC2-Describe')
    conn.remove_role_from_instance_profile(IAM_PROFILE, IAM_PROFILE)
    conn.delete_instance_profile(IAM_PROFILE)
    conn.delete_role(IAM_PROFILE)


def create_key_pairs():
    """Create key pairs for all users"""

    conn = _connect()

    with open(USER_FILE) as users:
        for user in users:
            user = user.split(',')[0].strip()

            # directory to store keys on host
            if not os.path.exists('/host/{0}/users/{1}'.format(VPC, user)):
                os.makedirs('/host/{0}/users/{1}'.format(VPC, user))

            if check_key_pair(user + '-{0}'.format(VPC)):
                if util.yn_prompt('Key pair exists. Delete and create a new one?'):
                    delete_key_pair(user + '-{0}'.format(VPC))
                else:
                    continue

            print "Creating key pair: {0} ...".format(user + '-{0}'.format(VPC))
            key = conn.create_key_pair(user + '-{0}'.format(VPC))
            key.save('/host/{0}/users/{1}'.format(VPC, user))

            # Generate ppk for Windows/PuTTY users
            os.system("puttygen /host/{1}/users/{0}/{0}-{1}.pem -o /host/{1}/users/{0}/{0}-{1}.ppk -O private".format(user, VPC))

            with open('/host/{0}/key-pairs.txt'.format(VPC), 'a') as f:
                f.write(user + '-' + VPC + '\n')

            print "Key '{0}' created and saved ...".format(user + '-{0}'.format(VPC))


def check_key_pair(user):
    """Check for existing user key pair"""

    conn = _connect()

    print "Checking for existing key pair: {0} ...".format(user)
    conn = boto.ec2.connect_to_region(AWS_REGION)
    if conn.get_all_key_pairs(filters = {'key-name': user}):
        return True


def delete_key_pair(user):
    """Delete a single key pair in AWS"""

    conn = _connect()

    print "Deleting key pair for user: {0} ...".format(user.strip())
    conn = _connect()
    conn.delete_key_pair(user)
    if os.path.exists('/host/{0}/users/{1}/{2}'.format(VPC, user, user + '-{0}.pem'.format(VPC))):
        os.remove('/host/{0}/users/{1}/{2}'.format(VPC, user, user + '-{0}.pem'.format(VPC)))
    if os.path.exists('/host/{0}/users/{1}/{2}'.format(VPC, user, user + '-{0}.ppk'.format(VPC))):
        os.remove('/host/{0}/users/{1}/{2}'.format(VPC, user, user + '-{0}.ppk'.format(VPC)))


def delete_key_pairs():
    """Delete all key pairs in AWS"""

    conn = _connect()

    with open('/host/{0}/key-pairs.txt'.format(VPC)) as users:
        for user in users:
            user = user.split(',')[0].strip()
            print "Deleting key pair for user: {0} ...".format(user.strip())
            conn.delete_key_pair(user)
            if os.path.exists('/host/{0}/{1}/{2}'.format(VPC, user, user + '-{0}.pem'.format(VPC))):
                os.remove('/host/{0}/{1}/{2}'.format(VPC, user, user + '-{0}.pem'.format(VPC)))


def get_vpc_id(conn, vpc_tag):
    """Return the vpc object queried by tag"""

    vpcs = conn.get_all_vpcs()

    for v in vpcs:
        if 'Name' in v.tags:
            if v.tags['Name'] == vpc_tag:
                return v


def get_starting_zone(subnets):
    """Return a starting zone number for current region"""
    zones = []
    for s in subnets:
        zones.append(s.availability_zone)

    zones.sort()
    for z in ZONES:
        if zones[0][-1] == z:
            return ZONES.index(z) + 1


def get_subnet_id(item, subnets):
    """Return the subnet id"""

    for sid in subnets:
        if sid.availability_zone[-1] == ZONES[item['ZONE']-1]:
            return sid.id

    # if we reach this point it means that the specified zone in instances.cfg
    # is not available in the current AWS_REGION so we default to the 'first' available
    for z in ZONES:
        for sid in subnets:
            if z == sid.availability_zone[-1]:
                return sid.id


def get_sg_ids(config, item, security_groups, VPC_TAG):
    """Return all security group id's"""

    sgs = []
    for sg in item['SECURITY_GROUPS']:
        for g in security_groups:
            if 'Name' in g.tags:
                if g.tags['Name'] == VPC_TAG + '-' + sg:
                    sgs.append(g.id)

    return sgs


def delete_amis():
    """Delete all images"""

    conn = boto.ec2.connect_to_region(AWS_REGION)
    images = conn.get_all_images(owners = ['self'])

    tag = TRAINER + '-{0}-'.format(VPC)

    for image in images:
        if image.name.startswith(tag):
            print 'Degristering {0} ...'.format(image.name)
            conn.deregister_image(image.id, delete_snapshot=True)


def terminate_environment(conn, user_vpc):
    """Terminates all instances, vpc, environment, and related training files"""

    print "Terminating environment ..."
    instances = inst.terminate_all_instances(conn, user_vpc)
    if instances:
        inst.confirm_terminated(instances)
    try:
        delete_iam_profile()
    except:
        print "WARNING: delete_iam_profile() failed"
        pass
    try:
        delete_key_pairs()
    except:
        print "WARNING: delete_key_pairs() failed"
        pass
    try:
        delete_amis()
    except:
        print "WARNING: delete_amis() failed"
        pass
    try:
        delete_vpc(user_vpc)
    except:
        print "WARNING: delete_vpcs() failed"
        pass
    try:
        if os.path.exists('/host/{0}'.format(VPC)):
            shutil.rmtree('/host/{0}'.format(VPC))
    except:
        print "WARNING: Removing directory '/host/{0}' failed".format(VPC)
        pass

    print "Environment deleted ..."
    print 'Finished ...'


def create_vpc():
    """Creates VPC with required configuration"""

    create_iam_profile()
    conn = _connect()
    vpc = _create_vpc(conn)
    gateway = _create_gateway(conn, vpc)
    route_table = _create_route_table(conn, vpc, gateway)
    _configure_network_acl(conn, vpc)
    _create_subnets(conn, vpc, route_table)
    _configure_default_security_group(conn, vpc)
