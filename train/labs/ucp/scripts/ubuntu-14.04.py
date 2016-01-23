#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    txt = 'docker run --rm --name ucp -v /var/run/docker.sock:/var/run/docker.sock docker/ucp install'
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

# docker cs release
wget -qO- 'https://pgp.mit.edu/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add --import
apt-get update
apt-get install -y apt-transport-https
echo "deb https://packages.docker.com/1.9/apt/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine

usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# packages
apt-get -y upgrade
apt-get install -y git tree jq xfsprogs linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# download/install upc
{0}

{{dinfo}}
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

# docker cs release
wget -qO- 'https://pgp.mit.edu/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add --import
apt-get update
apt-get install -y apt-transport-https
echo "deb https://packages.docker.com/1.9/apt/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine

usermod -aG docker ubuntu

# docker compose
curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# packages
apt-get -y upgrade
apt-get install -y git tree jq xfsprogs linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# download upc
docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images

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
    pass
