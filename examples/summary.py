#!/usr/bin/env python
'''
summary.py - This script displays summary of MRT format data.

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

import sys
from mrtparse import *
from datetime import datetime

summary = {}
start_time = end_time = 0

def count(d, k):
    try:
        d[k] += 1
    except KeyError:
        d[k] = 1

def total(d):
    if isinstance(d, int):
        return d
    n = 0
    for k in d:
        if isinstance(d[k], dict):
           n += total(d[k])
        else:
            n += d[k]
    return n

def print_line(lv, s, n):
    fmt = '%s%%-%ds%%8d' % (' ' * 4 * lv, 32 - 4 * lv)
    print(fmt % (s + ':', n))

def get_summary(f):
    global start_time, end_time

    d = Reader(f)
    m = d.next()
    start_time = end_time = m.mrt.ts

    d = Reader(f)
    for m in d:
        m = m.mrt

        if m.err:
            continue

        if m.ts < start_time:
            start_time = m.ts
        elif m.ts > end_time:
            end_time = m.ts

        if (   m.type == MRT_T['BGP4MP']
            or m.type == MRT_T['BGP4MP_ET']):
            if not m.type in summary:
                summary[m.type] = {}

            if (   m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
                or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
                or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
                or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):

                if not m.subtype in summary[m.type]:
                    summary[m.type][m.subtype] = {}
                count(summary[m.type][m.subtype], m.bgp.msg.type)

            elif ( m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
                or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):

                if not m.subtype in summary[m.type]:
                    summary[m.type][m.subtype] = {}
                count(summary[m.type][m.subtype], m.bgp.new_state)

            else:
                count(summary[m.type], m.subtype)
        else:
            if hasattr(m, 'subtype'):
                if not m.type in summary:
                    summary[m.type] = {}
                count(summary[m.type], m.subtype)
            else:
                count(summary, m.type)

def print_summary():
    print('[%s - %s]' % (
        datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')))

    for k1 in sorted(summary.keys()):
        print_line(0, MRT_T[k1], total(summary[k1]))

        if k1 == MRT_T['TABLE_DUMP']:
            for k2 in sorted(summary[k1].keys()):
                print_line(1, TD_ST[k2], total(summary[k1][k2]))

        elif k1 == MRT_T['TABLE_DUMP_V2']:
            for k2 in sorted(summary[k1].keys()):
                print_line(1, TD_V2_ST[k2], total(summary[k1][k2]))

        elif ( k1 == MRT_T['BGP4MP']
            or k1 == MRT_T['BGP4MP_ET']):

            for k2 in sorted(summary[k1].keys()):
                print_line(1, BGP4MP_ST[k2], total(summary[k1][k2]))

                if (   k2 == BGP4MP_ST['BGP4MP_MESSAGE']
                    or k2 == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
                    or k2 == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
                    or k2 == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
                    for k3 in sorted(summary[k1][k2].keys()):
                        print_line(2, BGP_MSG_T[k3], total(summary[k1][k2][k3]))

                elif ( k2 == BGP4MP_ST['BGP4MP_STATE_CHANGE']
                    or k2 == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
                    for k3 in sorted(summary[k1][k2].keys()):
                        print_line(2, BGP_FSM[k3], total(summary[k1][k2][k3]))

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    get_summary(sys.argv[1])
    print_summary()

if __name__ == '__main__':
    main()
