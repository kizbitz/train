#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.util import strtobool
import os
import sys
import toml

import boto.ec2
from boto.ec2.connection import EC2Connection

from config import *


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


def list_prompt(query, qlist):
    """Prompts for item from a list"""

    final = {}
    for n, i in enumerate(qlist, start=1):
        print " {0}) {1}".format(n,i)
        final[str(n)] = i
    answer = raw_input('\n' + query)

    try:
        int(answer)
    except ValueError:
        print '\nError: Invalid input\n'
        return list_prompt(query, qlist)
    try:
        final[answer]
    except KeyError:
        print '\nError: Invalid input\n'
        return list_prompt(query, qlist)

    return (final, answer)


def read_config(config):
    """Load toml config file"""

    try:
        with open(config) as c:
            return toml.loads(c.read())
    except IOError, e:
        print "Error reading config file: {0}".format(os.strerror(e.errno))
        sys.exit(e.errno)
