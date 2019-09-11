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

"""Interface for tracing package dependencies."""


class DependencyTracer(object):

    def trace_paths(self, start, target):
        raise NotImplementedError()


class Node(object):

    __slots__ = (
        'name',
        'node_type'
    )

    def __init__(self, name, node_type):
        self.name = name
        self.node_type = node_type

    def __key(self):
        return (self.name, self.node_type)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.__key() == other.__key()
        return NotImplemented


class Edge(object):

    __slots__ = (
        'start',
        'edge_type',
        'end',
    )

    def __init__(self, start, edge_type, end):
        self.start = start
        self.edge_type = edge_type
        self.end = end

    def __key(self):
        return (self.start, self.edge_type, self.end)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.__key() == other.__key()
        return NotImplemented


class TracerCache(object):
    """Caches edges and dead ends to target."""

    def __init__(self):
        # Key is (name, rawtype) value is True/False if node leads to target
        self._visited_nodes = {}  # type: Dict[(str, str), Optional[bool]]
        self._edges = {}  # type: Dict[(str, str), Set[(str, str)]]

    def visit(self, node):
        if node not in self._visited_nodes:
            self._visited_nodes[node] = None

    def check_visited(self, node):
        if node in self._visited_nodes:
            return True

    def check_leads_to_target(self, node):
        if node in self._visited_nodes:
            return self._visited_nodes[node]

    def check_fully_explored(self, node):
        if node in self._visited_nodes:
            return self._visited_nodes[node] is not None
        return False

    def edges(self, node):
        if node in self._edges:
            for edge in self._edges[node]:
                yield edge

    def recursive_edges(self, node):

        def _recursive_edges(node, edges):
            for edge in self.edges(node):
                if edge not in edges:
                    edges.add(edge)
                    _recursive_edges(edge.end, edges)

        edges = set()
        _recursive_edges(node, edges)
        for edge in edges:
            yield edge

    def add_edge(self, edge):
        if edge.start not in self._edges:
            self._edges[edge.start] = set()
        self._edges[edge.start].add(edge)

    def mark_leads_to_target(self, node, gets_there):
        self._visited_nodes[node] = gets_there
