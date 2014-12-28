#!/usr/bin/env python

from mrtparse import *
import sys

local_as = 12654
peer_as = {}
all_as = {}

def parse_as_path(m):
    if m.type != MSG_T['TABLE_DUMP_V2']:
        return

    if (     m.subtype != TD_V2_ST['RIB_IPV4_UNICAST']
         and m.subtype != TD_V2_ST['RIB_IPV6_UNICAST']):
        return             

    for attr in m.rib.entry[0].attr:
        if attr.type == BGP_ATTR_T['AS_PATH']: 
            as_path = attr.as_path
        elif attr.type == BGP_ATTR_T['AS4_PATH']: 
            as_path = attr.as4_path
        else:
            continue

        cur_as = local_as
        for path_seg in as_path:
            if path_seg['type'] == AS_PATH_SEG_T['AS_SET']:
                cur_as = 0
                continue
            l = path_seg['val'].split()
            for next_as in l:
                next_as = int(next_as)
                if cur_as == next_as:
                    continue
                elif cur_as < next_as and cur_as > 0 and next_as > 0:
                    try:
                        peer_as[cur_as][next_as] = 0
                    except:
                        peer_as[cur_as] = {next_as:0}
                elif cur_as > next_as and cur_as > 0 and next_as > 0:
                    try:
                        peer_as[next_as][cur_as] = 0
                    except:
                        peer_as[next_as] = {cur_as:0}
                cur_as = next_as

def print_html():
    node = ''
    link = ''
    count = 0
    for k1 in peer_as:
        if count > 10:
            break
        all_as[k1] = 0
        for k2 in peer_as[k1]:
            all_as[k2] = 0
            link += u'%s{source: %d, target: %d},\n' % (' ' * 12, k1, k2)
            count += 1
    for k in all_as:
        node += u'%s{id: %d, name: "AS%d"},\n' % (' ' * 12, k, k)

    print(u'''
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>mrtparse</title>
<style>
    .node {
        stroke: #fff;
        stroke-width: 1.5px;
    }
    .link {
        stroke: #999;
        stroke-opacity: .6;
    }
</style>
</head>
<body>
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script>
    var dataset = {
        nodes: [
%s
        ],
        links: [
%s
        ]
    }

    var width = 960;
    var height = 500;

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    var force = d3.layout.force()
        .nodes(dataset.nodes)
        .links(dataset.links)
        .charge(-200)
        .linkDistance(200)
        .size([width, height])
        .start();

    var link = svg.selectAll(".link")
        .data(dataset.links)
        .enter()
        .append("line")
        .attr("class", "link");

    var node = svg.selectAll(".node")
        .data(dataset.nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", 10)
        .style("fill", function(d) {
            if(d.sex == "M"){
                return "blue";
            }else{
                return "red";
            }
        })
        .call(force.drag);

    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
    });
</script>
</body>
</html>
    '''
    % (node, link))

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])
    for m in d:
        parse_as_path(m)

    f = open('test.out', 'w')
    for k1 in peer_as:
        line = '%d: ' % k1
        for k2 in peer_as[k1]:
            line += '%d ' % k2
        f.write('%s\n' % line)

    print_html()

if __name__ == '__main__':
    main()

