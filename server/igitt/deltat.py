#!/usr/bin/python3
#
# deltat.py — Parse a time duration
#
# License unknown, based on work by virhilo and Peter on Stackoverflow
# Modified by Marcel Waldvogel
#

import re
from datetime import timedelta


regex = re.compile(r'^((?P<days>[\.\d]+?)d)?'
                   r'((?P<hours>[\.\d]+?)h)?'
                   r'((?P<minutes>[\.\d]+?)m)?'
                   r'((?P<seconds>[\.\d]+?)s)?$')


def parse_time(time_str):
    """
    Parse a time string e.g. "2h13m" into a timedelta object.

    Based on Peter's answer at https://stackoverflow.com/a/51916936/2445204
    and virhilo's answer at https://stackoverflow.com/a/4628148/851699

    :param time_str: A string identifying a duration.  (eg. 2h13m)
    :return datetime.timedelta: A datetime.timedelta object
    """
    parts = regex.match(time_str)
    assert parts is not None, """Could not parse any time information from '{}'.
    Examples of valid strings: '8h', '2d8h5m20s', '2m4s'""".format(time_str)
    time_params = {name: float(param)
            for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)
