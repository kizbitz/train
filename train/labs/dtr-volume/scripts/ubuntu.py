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
curl -s https://packagecloud.io/install/repositories/Docker/cs-public/script.deb.sh | sudo bash
sleep 5
apt-get install -y tree xfsprogs linux-image-extra-$(uname -r)
apt-get install -y docker-engine-cs
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


# Notes
'''
Script requires:
    {fqdn}
    {dinfo}
'''
