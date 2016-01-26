#!/usr/bin/env python
# -*- coding: utf-8 -*-

PRIMARY_OS = 'Ubuntu-14.04'
PRIMARY = '''#!/bin/sh
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

# packages
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq xfsprogs linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# docker cs release
wget -qO- 'https://pgp.mit.edu/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add --import
apt-get update
apt-get install -y apt-transport-https
echo "deb https://packages.docker.com/1.9/apt/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine

usermod -aG docker ubuntu

# block device info
{dinfo}

# dtr
sudo bash -c "$(sudo docker run docker/trusted-registry install)"

# change storage location
service docker stop
rm -r /var/local/dtr/image-storage/local
ln -s /var/storage /var/local/dtr/image-storage/local
service docker start
'''


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass
