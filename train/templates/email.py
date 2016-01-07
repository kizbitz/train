#!/usr/bin/env python
# -*- coding: utf-8 -*-

# prompts
from_email = raw_input("Enter the 'from email address' for the outgoing message: ")
from_name =  raw_input("Enter the 'from name' for the outgoing message: ")
subject =  raw_input("Enter the 'Subject' for the outgoing message: ")

# static
text = """Welcome to Docker training!

This email contains files and other resources you need to complete the training.

**Do not delete this email until the training is done and completed.**

Once you enter the training area find a seat and connect to the internet either from the training room WiFi or other means before the class begins.

Once the class begins, we will walk through connecting to your assigned AWS instances.

We are looking forward to working with you!
"""
