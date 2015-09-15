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
