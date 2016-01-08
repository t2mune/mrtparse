#!/usr/bin/env python
'''
slice.py - This script slices MRT format data.

Copyright (C) 2016 greenHippo, LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Authors:
    Tetsumune KISO <t2mune@gmail.com>
    Yoshiyuki YAMAUCHI <info@greenhippo.co.jp>
    Nobuhiro ITOU <js333123@gmail.com>
'''

from mrtparse import *
import argparse, time, gzip, bz2, re
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(
        description='This script slices MRT format data.')
    parser.add_argument(
        'path_to_file',
        help='specify path to MRT format file')
    parser.add_argument(
        '-s', type=str, metavar='START_TIME', dest='start_time',
        help='specify start time in format YYYY-MM-DD HH:MM:SS')
    parser.add_argument(
        '-e', type=str, metavar='END_TIME', dest='end_time',
        help='specify end time in format YYYY-MM-DD HH:MM:SS')
    parser.add_argument(
        '-i', type=int, metavar='INTERVAL', dest='interval',
        help='specify interval in seconds')
    parser.add_argument(
        '-c', type=str, choices=['gz', 'bz2'], dest='compress_type',
        help='specify compress type (gz, bz2)')
    return parser.parse_args()

def conv_unixtime(t):
    try:
        t = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        t = int(time.mktime(t.timetuple()))
    except TypeError:
        t = None
    except ValueError:
        print('error: invalid time \'%s\'' % t)
        exit(1)

    return t

def file_open(f, t, c):
    f = re.sub(r'.gz$|.bz2$', '', f)
    t = datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
    if c is None:
        return open('%s-%s' % (f, t), 'wb')
    elif c == 'gz':
        return gzip.GzipFile('%s-%s.%s' % (f, t, c), 'wb')
    elif c == 'bz2':
        return bz2.BZ2File('%s-%s.%s' % (f, t, c), 'wb')

def slice_mrt(args):
    t = start_time = conv_unixtime(args.start_time)
    end_time = conv_unixtime(args.end_time)
    interval = args.interval

    if t is None:
        d = Reader(args.path_to_file)
        m = d.next()
        t = m.mrt.ts

    f = file_open(args.path_to_file, t, args.compress_type)
    d = Reader(args.path_to_file)
    for m in d:
        m = m.mrt
        if start_time and (m.ts < start_time):
            continue
        if end_time and (m.ts >= end_time):
            break
        if interval and (m.ts >= t + interval):
            f.close()
            t += interval
            f = file_open(args.path_to_file, t, args.compress_type)
        f.write(m.buf)
    f.close()

def main():
    args = parse_args()
    slice_mrt(args)

if __name__ == '__main__':
    main()
