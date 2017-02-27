#!/usr/bin/env python
# -*- coding: utf-8 -*-

# instance configs
PRIMARY_OS = 'Ubuntu-16.04'
PRIMARY = '''#!/bin/sh

FQDN="{fqdn}"

export DEBIAN_FRONTEND=noninteractive

# locale
sudo locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# required packages
apt-get update
apt-get install -y -q slapd ldap-utils phpldapadmin

# config files - temp solution
curl -sSL https://gist.githubusercontent.com/kizbitz/f2e10ccdbf9db4bbbe7262d9e5fc09ff/raw/af233a12e78851399e1d7e8ea8bc2758bcea6f0a/docker-ldap-training-configs.sh | sh

# final prep
chown root:www-data /etc/phpldapadmin/config.php
rm -r /var/lib/ldap/*
rm -r /etc/ldap/slapd.d/*
slapadd -F /etc/ldap/slapd.d -b cn=config -l /tmp/config.ldif
slapadd -l /tmp/data.ldif
chown -R openldap:openldap /etc/ldap/slapd.d
chown -R openldap:openldap /var/lib/ldap

service slapd restart
service apache2 restart

{dinfo}
'''

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh

FQDN="{fqdn}"

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

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
