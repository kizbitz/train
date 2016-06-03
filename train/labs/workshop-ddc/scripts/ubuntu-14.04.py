#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from distutils.util import strtobool

# Preinstall UCP for the Dockercon training classes
txt = 'docker run --rm --name ucp -v /var/run/docker.sock:/var/run/docker.sock docker/ucp install --host-address $(curl http://169.254.169.254/latest/meta-data/public-ipv4)'

# scripts
PRIMARY_OS = 'Ubuntu-14.04'
CONTROLLER = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# docker
curl -sSL https://get.docker.com/ | sh

usermod -aG docker ubuntu

# updates
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.6.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# download/install upc
{0}

{{dinfo}}

reboot
'''.format(txt)


NODE = '''#!/bin/sh

FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# updates
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# docker
curl -sSL https://get.docker.com/ | sh

usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.6.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# download upc
docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images

{dinfo}

reboot
'''

DTR = '''#!/bin/sh

FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# updates/docker cs engine
wget -qO- 'https://pgp.mit.edu/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add --import
echo "deb https://packages.docker.com/1.10/apt/repo ubuntu-trusty main" | sudo tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get -y upgrade
apt-get install -y \
    apt-transport-https \
    docker-engine \
    git \
    tree \
    jq \
    linux-image-extra-4.2.0-23-generic \
    linux-image-4.2.0.23-generic \
    linux-image-extra-virtual

usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.6.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# dtr
bash -c "$(sudo docker run docker/trusted-registry install)"

{dinfo}

reboot
'''

LDAP_OS = 'JTU-LDAP'
LDAP = '''#!/bin/sh

FQDN="{fqdn}"

{dinfo}
'''

AMIBUILD = '''#!/bin/sh
#
FQDN="{{fqdn}}"

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

{{dinfo}}
reboot
'''


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
