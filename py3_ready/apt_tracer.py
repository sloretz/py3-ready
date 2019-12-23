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

"""Tools for walking through and tracing debian package dependencies.""" 

from __future__ import print_function

import copy
import sys

from .dependency_tracer import DependencyTracer
from .dependency_tracer import Edge
from .dependency_tracer import Node
from .dependency_tracer import TracerCache
from .dot import paths_to_dot

from apt.cache import Cache
from apt.package import Package

APT_NODE = 'apt'


class AptTracer(DependencyTracer):

    def __init__(self, apt_cache=None, quiet=True):
        if not apt_cache:
            apt_cache = Cache()
        self._apt_cache = apt_cache
        self._quiet = quiet

    def trace_paths(self, start, target, cache=None):
        if start in self._apt_cache:
            start_pkg = self._apt_cache[start]
        else:
            msg = "'{}' not in apt cache.".format(start)
            if not self._quiet:
                sys.stderr.write(msg + '\n')
            raise KeyError(msg)
        if target in self._apt_cache:
            target_pkg = self._apt_cache[target]
        else:
            msg = "'{}' not in apt cache.".format(target)
            if not self._quiet:
                sys.stderr.write(msg + '\n')
            raise KeyError(msg)

        self._edges_to_target = []
        self._deferred_pkgs = set()
        if not cache:
            cache = TracerCache()
        self._cache = cache

        # Descend through dependency
        self._trace_path(start_pkg, target_pkg)
        # Need extra passes for circular dependencies
        while self._deferred_pkgs:
            def_pkgs = self._deferred_pkgs
            self._deferred_pkgs = set()
            for def_pkg in def_pkgs:
                self._trace_path(def_pkg, target_pkg)
        # TODO(sloretz) why are edges sometimes repeated?
        return list(set(self._edges_to_target))

    def _trace_path(self, start, target):
        """Depth first search to trace paths to target."""
        if start.name == target.name:
            # Found target
            return True
        start_node = Node(start.name, APT_NODE)
        if self._cache.check_visited(start_node):
            if self._cache.check_fully_explored(start_node):
                leads_to_target = self._cache.check_leads_to_target(start_node)
                if leads_to_target:
                    self._edges_to_target.extend(self._cache.recursive_edges(start_node))
                return leads_to_target
            else:
                # Defer checks on circular dependencies
                self._deferred_pkgs.add(start)
                return False
        self._cache.visit(start_node)
        if not start.candidate.dependencies:
            # lowest level and target not found
            self._cache.mark_leads_to_target(start_node, False)
            return False
        leads_to_target = False
        for dependency in start.candidate.dependencies:
            # Check all the candidates that can satisfy this dependency
            for base_dep in dependency:
                # Only walk upstream dependencies
                if base_dep.rawtype in ['Depends', 'PreDepends', 'Suggests', 'Recommends']:
                    if self._apt_cache.is_virtual_package(base_dep.name):
                        virtual_to_target = False
                        base_dep_node = Node(base_dep.name, APT_NODE)
                        for pkg in self._apt_cache.get_providing_packages(base_dep.name):
                            if self._trace_path(pkg, target):
                                leads_to_target = True
                                edge1 = Edge(start_node, base_dep.rawtype, base_dep_node)
                                pkg_node = Node(pkg.name, APT_NODE)
                                edge2 = Edge(base_dep_node, 'virtual', pkg_node)
                                self._cache.add_edge(edge1)
                                self._cache.add_edge(edge2)
                                self._edges_to_target.append(edge1)
                                self._edges_to_target.append(edge2)
                                virtual_to_target = True
                        self._cache.mark_leads_to_target(base_dep_node, virtual_to_target)
                    else:
                        if base_dep.name in self._apt_cache:
                            pkg = self._apt_cache[base_dep.name]
                        else:
                            if not self._quiet:
                                sys.stderr.write(
                                    "'{}' not in apt cache. Used by '{}' as '{}'\n".format(
                                        base_dep.name, start.name, dependency))
                            continue
                        if self._trace_path(pkg, target):
                            leads_to_target = True
                            pkg_node = Node(pkg.name, APT_NODE)
                            edge = Edge(start_node, base_dep.rawtype, pkg_node)
                            self._cache.add_edge(edge)
                            self._edges_to_target.append(edge)
        self._cache.mark_leads_to_target(start_node, leads_to_target)
        return leads_to_target


APT_EDGE_LEGEND = {
    'virtual': '[color=green]',
    'Depends': '[color=blue]',
    'PreDepends': '[color=blue]',
    'Suggests': '[color=yellow]',
    'Recommends': '[color=yellow]',
}


class AptTracerCommand(object):

    COMMAND_NAME='check-apt'
    COMMAND_HELP='check if apt package depends on python 2'

    def __init__(self, parser):
        # arguments for start, target, quiet, and dot output
        # Add arguments to arg-parser
        parser.add_argument(
            'pkg', type=str,
            help='Name of package to check for dependency on python 2')
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument(
            '--dot', action='store_true', help='output DOT graph')
        parser.add_argument(
            '--target', default='python',
            help='Package to trace to (default python)')

    def do_command(self, args):
        start = args.pkg
        target = args.target

        tracer = AptTracer(quiet=args.quiet)

        try:
            paths = tracer.trace_paths(start, target)
        except KeyError:
            return 2

        if args.dot:
            print(paths_to_dot(paths, edge_legend=APT_EDGE_LEGEND))
        elif not args.quiet:
            if paths:
                print('{} depends on {}'.format(start, target))
            else:
                print('{} does not depend on {}'.format(start, target))

        if paths:
            # non-zero exit code to indicate it does depend on target
            # because it's assumed depending on target is undesirable
            return 1
        return 0
