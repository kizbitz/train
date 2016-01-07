#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass

def prompt_pass(question):
    pass1 = getpass.getpass(question)
    pass2 = getpass.getpass("Confirm password: ")

    if pass1 != pass2:
        prompt_pass(question)
    else:
        return pass1


# prompts
ubuntu_pass = prompt_pass("Enter 'ubuntu' password for nodes: ")
hub_name = raw_input("Enter your Docker Hub username: ")
hub_pass = prompt_pass("Enter your Docker Hub password: ")
hub_email = raw_input("Enter your Docker Hub email: ")


# scripts
PRIMARY_OS = 'Ubuntu-14.04'
PRIMARY = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# required packages
apt-get update
apt-get -y upgrade
apt-get install -y git tree linux-image-extra-3.19.0-26-generic linux-image-3.19.0-26-generic

# password authentication
echo ubuntu:{0} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

# docker
curl -sSL https://get.docker.com/ | sh
usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# pull the ucp images
docker login --username="{1}" --password="{2}" --email="{3}"

docker pull dockerorca/ucp-controller
docker pull dockerorca/ucp
docker pull dockerorca/ucp-cfssl
docker pull dockerorca/ucp-cfssl-proxy
docker pull dockerorca/ucp-proxy
docker pull swarm
docker pull dockerorca/ucp-etcd
docker pull dockerorca/dsinfo

{{dinfo}}
reboot
'''.format(ubuntu_pass, hub_name, hub_pass, hub_email)


AMIBUILD = '''#!/bin/sh
#
FQDN="{{fqdn}}"

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# password authentication
echo ubuntu:{0} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

{{dinfo}}
reboot
'''.format(ubuntu_pass)


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass
