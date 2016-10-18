#!/usr/bin/env python
# -*- coding: utf-8 -*-

# prompts
ubuntu_pass = raw_input("Enter password for 'ubuntu' user: ")

# scripts
PRIMARY_OS = 'Ubuntu-14.04'
PRIMARY = '''#!/bin/sh
#
FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# /etc/hostname - /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

# docker os release
curl -sSL https://get.docker.com/ | sh

# docker cs release
#wget -qO- 'https://pgp.mit.edu/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add --import
#apt-get update
#apt-get install -y apt-transport-https
#echo "deb https://packages.docker.com/1.9/apt/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
#apt-get update
#apt-get install -y docker-engine

usermod -aG docker ubuntu

# updates
apt-get update
apt-get -y upgrade
apt-get install -y git tree jq linux-image-extra-4.2.0-30-generic linux-image-4.2.0-30-generic

# compose
curl -L https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# password authentication
echo ubuntu:{0} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

# cleanup.sh
# ==========
cat >/home/ubuntu/cleanup.sh <<EOL
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

chmod +x /home/ubuntu/cleanup.sh
chown ubuntu:ubuntu /home/ubuntu/cleanup.sh

service docker stop
rm -r /var/lib/docker
rm /etc/docker/key.json
cp /etc/default/docker /etc/default/docker.bak

{{dinfo}}
reboot
'''.format(ubuntu_pass)


# Script to use if launching from a custom lab AMI image
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

service docker stop
rm -r /var/lib/docker
rm /etc/docker/key.json

{{dinfo}}
reboot
'''.format(ubuntu_pass)


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass
