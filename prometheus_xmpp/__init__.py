#!/usr/bin/python3
# Simple HTTP web server that forwards prometheus alerts over XMPP.
#
# To use, configure a web hook in alertmanager. E.g.:
#
# receivers:
# - name: 'jelmer-pager'
#   webhook_configs:
#   - url: 'http://192.168.2.1:9199/alert'
#
# Edit xmpp-alerts.yml.example, then run:
# $ python3 prometheus-xmpp-alerts --config=xmpp-alerts.yml.example

import re
from datetime import datetime
import subprocess


__version__ = (0, 3, 2)
version_string = '.'.join(map(str, __version__))


def parse_timestring(ts):
    # strptime doesn't understand nanoseconds, so discard the last three digits
    # also convert timezone from hh:mm to hhmm
    tsc = re.sub('\\.(\d{6})(\d{3})([+-])(\d\d):(\d\d)', r'.\1\3\4\5', ts)
    return datetime.strptime(tsc, '%Y-%m-%dT%H:%M:%S.%f%z')


def create_message(message):
    """Create the message to deliver."""
    for alert in message['alerts']:
        annotations = alert.get('annotations')
        yield '%s, %s, %s' % (
            message['status'].upper(),
            parse_timestring(alert['startsAt']).isoformat(timespec='seconds'),
            annotations.get('summary') if annotations else '')


def run_amtool(args):
    """Run amtool with the specified arguments."""
    # TODO(jelmer): Support setting the current user, e.g. for silence ownership.
    ret = subprocess.run(
        ["/usr/bin/amtool"] + args, shell=False, text=True,
        stdout=subprocess.PIPE)
    return ret.stdout
