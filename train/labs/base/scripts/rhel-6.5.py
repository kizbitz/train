#!/usr/bin/env python

PRIMARY_OS = 'RHEL-6.5'
PRIMARY = '''#!/bin/sh
#
FQDN="{fqdn}"

# /etc/hostname - /etc/hosts
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts
echo $FQDN > /etc/hostname
service hostname restart
sleep 5

{dinfo}
'''

def pre_process():
    """Anything added to this function is executed before launching the instances"""
    pass

def post_process():
    """Anything added to this function is executed after launching the instances"""
    pass
