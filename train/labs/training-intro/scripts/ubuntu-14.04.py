#!/usr/bin/env python
# -*- coding: utf-8 -*-

# prompts

# instance configs
PRIMARY_OS = 'Ubuntu-14.04'
PRIMARY = '''#!/bin/sh

FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# docker os release
curl -sSL https://get.docker.com/ | sh

usermod -aG docker ubuntu

# updates
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq linux-image-extra-4.2.0-23-generic linux-image-4.2.0.23-generic

# compose
curl -L https://github.com/docker/compose/releases/download/1.7.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# output cleanup script
cat >/usr/local/bin/docker-reset <<EOL
#!/bin/bash
sudo service docker stop
# /etc/default/docker
sudo rm /etc/default/docker
sudo cp /etc/default/docker.bak /etc/default/docker
unset -v DOCKER_HOST
unset -v DOCKER_OPTS
unset -v DOCKER_CONTENT_TRUST
sudo rm -r /var/lib/docker
sudo service docker start
EOL

chmod +x /usr/local/bin/docker-reset

service docker stop
rm -r /var/lib/docker
rm /etc/docker/key.json
cp /etc/default/docker /etc/default/docker.bak
service docker start

{dinfo}
'''

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh

FQDN="{fqdn}"

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

{dinfo}
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
