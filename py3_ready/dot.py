# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def paths_to_dot(paths, edge_legend=None, node_legend=None):
    """Given dependency paths, output in dot format for graphviz."""
    if edge_legend is None:
        edge_legend = {}
    if node_legend is None:
        node_legend = {}
    edges = []
    nodes = set()
    for edge in paths:
        style = ''
        if edge.edge_type in edge_legend:
            style = edge_legend[edge.edge_type]
        edges.append('  "{beg}%{begtype}" -> "{end}%{endtype}"{style};  // {rawtype}\n'.format(
            beg=edge.start.name,
            begtype=edge.start.node_type,
            end=edge.end.name,
            endtype=edge.end.node_type,
            style=style,
            rawtype=edge.edge_type))
        nodes.add(edge.start)
        nodes.add(edge.end)
    node_dot = []
    for node in nodes:
        style = ''
        if node.node_type in node_legend:
            style = node_legend[node.node_type]
        node_dot.append('  "{name}%{ntype}"{style}[label="{name}"];  // {ntype}\n'.format(
            name=node.name, style=style, ntype=node.node_type))

    return 'digraph G {{\n{edges}\n{nodes}}}'.format(
        edges=''.join(edges),
        nodes=''.join(node_dot))
