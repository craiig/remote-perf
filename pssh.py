#!/Users/craig/Dropbox/School-UBC/SparkAWS/venv/bin/python
# -*- Mode: python -*-

# Copyright (c) 2009-2012, Andrew McNabb
# Copyright (c) 2003-2008, Brent N. Chun

"""Parallel ssh to the set of nodes in hosts.txt.
modified by Craig Mustard to better support running perf remotely
requires pssh at https://github.com/craiig/parallel-ssh

For each node, this essentially does an "ssh host -l user prog [arg0] [arg1]
...". The -o option can be used to store stdout from each remote node in a
directory.  Each output file in that directory will be named by the
corresponding remote node's hostname or IP address.
"""

import fcntl
import os
import sys
import signal

parent, bindir = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
if os.path.exists(os.path.join(parent, 'psshlib')):
    sys.path.insert(0, parent)

from psshlib import psshutil
from psshlib.manager import Manager, FatalError
from psshlib.task import Task
from psshlib.cli import common_parser, common_defaults

_DEFAULT_TIMEOUT = 0

def option_parser():
    parser = common_parser()
    parser.usage = "%prog [OPTIONS] command [...]"
    parser.epilog = "Example: pssh -h hosts.txt -l irb2 -o /tmp/foo uptime"

    parser.add_option('-i', '--inline', dest='inline', action='store_true',
            help='inline aggregated output and error for each server')
    parser.add_option('--inline-stdout', dest='inline_stdout',
            action='store_true',
            help='inline standard output for each server')
    parser.add_option('-I', '--send-input', dest='send_input',
            action='store_true',
            help='read from standard input and send as input to ssh')
    parser.add_option('-P', '--print', dest='print_out', action='store_true',
            help='print output as we get it')
    parser.add_option('--soft_kill', dest='soft_kill', action='store_true',
            help='write ctrl+c char (0x03) to processes instead of sending SIGKILL on termination')

    return parser

def parse_args():
    parser = option_parser()
    defaults = common_defaults(timeout=_DEFAULT_TIMEOUT)
    parser.set_defaults(**defaults)
    opts, args = parser.parse_args()

    if len(args) == 0 and not opts.send_input:
        parser.error('Command not specified.')

    if not opts.host_files and not opts.host_strings:
        parser.error('Hosts not specified.')

    return opts, args

def do_pssh(hosts, cmdline, opts):
    if opts.outdir and not os.path.exists(opts.outdir):
        os.makedirs(opts.outdir)
    if opts.errdir and not os.path.exists(opts.errdir):
        os.makedirs(opts.errdir)
    if opts.send_input:
        stdin = sys.stdin.read()
    else:
        stdin = None
    manager = Manager(opts)
    for host, port, user in hosts:
        cmd = ['ssh', host, '-o', 'NumberOfPasswordPrompts=1',
                '-o', 'SendEnv=PSSH_NODENUM PSSH_HOST', '-t', '-t']
        if opts.options:
            for opt in opts.options:
                cmd += ['-o', opt]
        if user:
            cmd += ['-l', user]
        if port:
            cmd += ['-p', port]
        if opts.extra:
            cmd.extend(opts.extra)
        if cmdline:
            cmd.append(cmdline)
        t = Task(host, port, user, cmd, opts, stdin)
        manager.add_task(t)
    try:
        statuses = manager.run()
    except FatalError:
        sys.exit(1)

    if min(statuses) < 0:
        # At least one process was killed.
        sys.exit(3)
    # The any builtin was introduced in Python 2.5 (so we can't use it yet):
    #elif any(x==255 for x in statuses):
    for status in statuses:
        if status == 255:
            sys.exit(4)
    for status in statuses:
        if status != 0:
            sys.exit(5)

if __name__ == "__main__":
    #trap keyboardinterrupt
    # so we can cleanly shut down
    def sigint_handler(signal, frame):
        print "kill all ssh sessions lol"

    # signal.signal(signal.SIGINT, sigint_handler)

    opts, args = parse_args()
    cmdline = " ".join(args)
    
    try:
        hosts = psshutil.read_host_files(opts.host_files,
            default_user=opts.user)
    except IOError:
        _, e, _ = sys.exc_info()
        sys.stderr.write('Could not open hosts file: %s\n' % e.strerror)
        sys.exit(1)
    if opts.host_strings:
        for s in opts.host_strings:
            hosts.extend(psshutil.parse_host_string(s, default_user=opts.user))
    do_pssh(hosts, cmdline, opts)
