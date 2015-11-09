#!/usr/bin/env python

"""
Given a list of ip/hosts to connect to:

Setup:
Connect to them and install perf, waiting until all machines have succeeded

Measure:
Connect to all machines and start perf
Wait for ctrl+c from script - or until a time? or another event? maybe wait for a local process to finish!!!

Collect:
Connect to all machines and download the most recent perf log
"""

from psshlib import psshutil
from psshlib.manager import Manager, FatalError
from psshlib.task import Task
from psshlib.cli import common_parser, common_defaults

import boto3
import argparse
import signal

#trap keyboardinterrupt
# so we can cleanly shut down
def sigint_handler(signal, frame):
    print "kill all ssh sessions lol"

signal.signal(signal.SIGINT, sigint_handler)

#parse those argments
#parser = argparse.ArgumentParser()
# parser.add_argument('-H', '--host_files', type=lambda x: x.split(','), required=True)
# parser.add_argument('-u', '--user', type=str, default="root")
# opts  = parser.parse_args()
# print opts
parser = common_parser()
opts, args = parse_args():

# read a hosts file
hosts = psshutil.read_host_files(opts.host_files,
    default_user=opts.user)
# hosts = [h.strip() for h in opts.hosts_file]

cmdline = "perf...."



