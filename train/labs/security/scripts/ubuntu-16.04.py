#!/usr/bin/env python

# scripts
PRIMARY_OS = 'Ubuntu-16.04'
PRIMARY = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# packages
curl -s 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | apt-key add --import
echo "deb https://packages.docker.com/1.13/apt/repo ubuntu-xenial main" | tee /etc/apt/sources.list.d/docker.list
apt-get update && apt-get install -y \
    apt-transport-https \
    docker-engine \
    git \
    htop \
    jq \
    inux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    seccomp \
    strace \
    tree

usermod -aG docker ubuntu

# compose
curl -L https://github.com/docker/compose/releases/download/1.11.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

{{dinfo}}
reboot
'''.format()

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh

FQDN="{{fqdn}}"

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

{{dinfo}}
reboot
'''.format()

def pre_process():
    """Anything added to this function is executed before launching the instances"""
    pass

def post_process():
    """Anything added to this function is executed after launching the instances"""
    pass
