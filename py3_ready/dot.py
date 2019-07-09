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


def paths_to_dot(paths, edge_legend=None):
    """Given dependency paths, output in dot format for graphviz."""
    if edge_legend is None:
        edge_legend = {}
    edges = []
    for edge in paths:
        style = ''
        if edge.edge_type in edge_legend:
            style = edge_legend[edge.edge_type]
        edges.append('  "{beg}" -> "{end}"{style};  // {rawtype}\n'.format(
            beg=edge.start.name,
            end=edge.end.name,
            style=style,
            rawtype=edge.edge_type))

    return 'digraph G {{\n{edges}}}'.format(edges=''.join(edges))
