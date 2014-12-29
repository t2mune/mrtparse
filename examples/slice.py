#!/usr/bin/env python
'''
slice.py - a script to create a configuration file for exabgp using mrtparse.

Copyright (C) 2014 greenHippo, LLC.

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
import argparse, time, gzip, bz2
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='This script slices MRT format data.')
    parser.add_argument('-s', '--start-time', type=str,
        help='specifies the end time in format YYYY-MM-DD HH:MM:SS')
    parser.add_argument('-e', '--end-time', type=str,
        help='specifies the start time in format YYYY-MM-DD HH:MM:SS')
    parser.add_argument('-i', '--interval', type=int,
        help='specifies the interval in seconds')
    parser.add_argument('-c', '--compress-type', type=str, choices=['gz', 'bz2'],
        help='specifies the compress type (gz, bz2)')
    parser.add_argument('-f', '--filename', type=str, required=True,
        help='a file path to MRT format data')
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
        d = Reader(args.filename)
        m = d.next()
        t = m.mrt.ts

    f = file_open(args.filename, t, args.compress_type)
    d = Reader(args.filename)
    for m in d:
        if start_time and (m.mrt.ts < start_time):
            continue
        if end_time and (m.mrt.ts > end_time):
            break
        if interval and (m.mrt.ts >= t + interval):
            f.close()
            t += interval
            f = file_open(args.filename, t, args.compress_type)
        f.write(m.buf)
    f.close()

def main():
    args = parse_args()
    slice_mrt(args)

if __name__ == '__main__':
    main()
