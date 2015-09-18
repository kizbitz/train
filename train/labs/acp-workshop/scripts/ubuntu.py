#!/usr/bin/env python
# -*- coding: utf-8 -*-

PRIMARY_OS = 'Ubuntu-14.04'
CS_ENGINE = '''#!/bin/sh
#
FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

apt-get update
apt-get -y upgrade
apt-get install -y linux-image-extra-virtual

{dinfo}
reboot
'''

OS_ENGINE = '''#!/bin/sh
#
FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

curl -sSL https://get.docker.com/ | sh
usermod -aG docker ubuntu

{dinfo}
reboot
'''

def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass


# Notes
'''
Script requires:
    {fqdn}
    {dinfo}
'''
