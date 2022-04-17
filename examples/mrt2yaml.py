#!/usr/bin/env python

import yaml
import sys
import collections
from mrtparse import *

def represent_ordereddict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

yaml.add_representer(collections.OrderedDict, represent_ordereddict)

#import yaml
#
#_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
#
#def dict_representer(dumper, data):
#    return dumper.represent_dict(data.iteritems())
#
#def dict_constructor(loader, node):
#    return collections.OrderedDict(loader.construct_pairs(node))

def main():
    print('---')
    for entry in Reader(sys.argv[1]):
        print(yaml.dump([entry.data])[:-1])


if __name__ == '__main__':
    main()
