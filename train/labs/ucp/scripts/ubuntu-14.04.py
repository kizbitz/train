#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from distutils.util import strtobool

def yn_prompt(query):
    """Generic Y/N Prompt"""

    sys.stdout.write('%s [y/n]: ' % query)
    val = raw_input()
    try:
        ret = strtobool(val)
    except ValueError:
        sys.stdout.write('Please answer with a y/n\n')
        return yn_prompt(query)
    return ret


# prompts
install = yn_prompt("\nInstall UCP using 'non-interactive' mode on the controller instance?")

if install:
    txt = 'docker run --rm --name ucp -v /var/run/docker.sock:/var/run/docker.sock docker/ucp install --host-address $(curl http://169.254.169.254/latest/meta-data/public-hostname)'
else:
    txt = 'docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images'


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

# updates
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.6.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# packages
apt-get install -y git tree jq

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

# packages
apt-get install -y git tree jq

# download upc
docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images

{dinfo}

reboot
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
    print "Instances Launched ...\n\nNOTE: If you selected the non-interactive install during launch the default user/pass is: admin/orca\n"
