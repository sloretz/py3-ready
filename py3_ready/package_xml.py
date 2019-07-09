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

"""Tools for checking dependencies of package.xml files."""

from __future__ import print_function

import os
import sys

from .apt_tracer import APT_EDGE_LEGEND
from .dependency_tracer import DependencyTracer
from .dependency_tracer import Edge
from .dependency_tracer import Node
from .dependency_tracer import TracerCache
from .dot import paths_to_dot
from .rosdep import is_rosdep_initialized
from .rosdep import ROSDEP_EDGE_LEGEND
from .rosdep import ROSDEP_NODE
from .rosdep import ROSDEP_NODE_LEGEND
from .rosdep import RosdepTracer

from apt.cache import Cache
from catkin_pkg.package import parse_package
from catkin_pkg.packages import find_packages


PACKAGE_NODE='package'


class PackageCache(object):

    def __init__(self):
        # Key: name, Value: parsed package xml file
        self._packages = self._find_packages(self._get_search_paths())

    def _get_search_paths(self):
        env_vars = (
            'AMENT_PREFIX_PATH',
            'CMAKE_PREFIX_PATH',
            'COLCON_PREFIX_PATH'
        )
        paths = []
        for var in env_vars:
            text = os.getenv(var, default='')
            for path in text.split(':'):
                if path:
                    yield path

    def _find_packages(self, search_paths):
        packages = {}
        for path in search_paths:
            for path, pkg in find_packages(path).items():
                # TODO(sloretz) is this doing overlay workspaces correctly?
                packages[pkg.name] = pkg
        return packages

    def find_package(self, name):
        if name in self._packages:
            return self._packages[name]



class PackageXMLTracer(DependencyTracer):

    def __init__(self, apt_cache=None, quiet=True):
        self._quiet = quiet
        self._tracer = RosdepTracer(apt_cache=apt_cache, quiet=self._quiet)
        self._package_cache = PackageCache()

    def trace_paths(self, start, target, cache=None):
        # start: path to a ROS package
        # target: name of a debian package
        start_pkg = parse_package(start)

        if not cache:
            cache = TracerCache()
        self._cache = cache

        self._visited_pkgs = []
        self._deferred_pkgs = set()
        self._pkgs_to_target = set([])
        self._visited_rosdeps = []
        self._rosdeps_to_target = set([])

        self._trace_path(start_pkg, target)
        # Need extra passes for circular dependencies
        while self._deferred_pkgs:
            def_pkgs = self._deferred_pkgs
            self._deferred_pkgs = set()
            for def_pkg in def_pkgs:
                self._trace_path(def_pkg, target)
        start_node = Node(start_pkg.name, PACKAGE_NODE)
        return list(set(self._cache.recursive_edges(start_node)))

    def _trace_path(self, start, target):
        """return true if path leads to target debian package"""
        start_node = Node(start.name, PACKAGE_NODE)
        if self._cache.check_visited(start_node):
            if self._cache.check_fully_explored(start_node):
                leads_to_target = self._cache.check_leads_to_target(start_node)
                return leads_to_target
            else:
                # Defer checks on circular dependencies
                self._deferred_pkgs.add(start)
                return False
        self._cache.visit(start_node)

        depends = []
        for dep in start.build_depends:
            depends.append((dep, 'build_depend'))
        for dep in start.buildtool_depends:
            depends.append((dep, 'buildtool_depend'))
        for dep in start.build_export_depends:
            depends.append((dep, 'build_export_depend'))
        for dep in start.buildtool_export_depends:
            depends.append((dep, 'buildtool_export_depend'))
        for dep in start.exec_depends:
            depends.append((dep, 'exec_depend'))
        for dep in start.test_depends:
            depends.append((dep, 'test_depend'))
        for dep in start.doc_depends:
            depends.append((dep, 'doc_depend'))
        for dep in start.group_depends:
            depends.append((dep, 'group_depend'))

        rosdep_keys = []
        for dep, _ in depends:
            if self._package_cache.find_package(dep.name) is None:
                rosdep_keys.append(dep.name)

        leads_to_target = False
        for dep, rawtype in depends:
            if dep.name in rosdep_keys:
                dep_node = Node(dep.name, ROSDEP_NODE)
                dep_leads_to_target = False
                if self._cache.check_fully_explored(dep_node):
                    dep_leads_to_target = self._cache.check_leads_to_target(dep_node)
                else:
                    # Trace rosdep key to target
                    rosdep_paths = self._tracer.trace_paths(dep.name, target, cache=self._cache)
                    if rosdep_paths:
                        dep_leads_to_target = True
                if dep_leads_to_target:
                    leads_to_target = True
                    edge = Edge(
                        start_node,
                        rawtype,
                        dep_node
                    )
                    self._cache.add_edge(edge)
                    leads_to_target = True
            else:
                pkg = self._package_cache.find_package(dep.name)
                if pkg is None and not self._quiet:
                    sys.stderr.write('Failed to find package or rosdep key [{}]\n'.format(dep.name))
                dep_node = Node(dep.name, PACKAGE_NODE)
                if self._trace_path(pkg, target):
                    edge = Edge(start_node, rawtype, dep_node)
                    self._cache.add_edge(edge)
                    leads_to_target = True

        self._cache.mark_leads_to_target(start_node, leads_to_target)
        return leads_to_target


PACKAGE_XML_EDGE_LEGEND = {
    'build_depend': '[color=pink]',
    'buildtool_depend': '[color=pink]',
    'build_export_depend': '[color=pink]',
    'buildtool_export_depend': '[color=pink]',
    'exec_depend': '[color=pink]',
    'test_depend': '[color=pink]',
    'doc_depend': '[color=pink]',
    'group_depend': '[color=pink]',
}

PACKAGE_XML_NODE_LEGEND = {
    PACKAGE_NODE: '[color=pink,shape=hexagon]'
}


class CheckPackageXMLCommand(object):
    COMMAND_NAME='check-package-xml'
    COMMAND_HELP='check if dependencies in a package.xml depend on python 2'

    def __init__(self, parser):
        # arguments for key, quiet, and dot output
        parser.add_argument(
            'path', type=str,
            help='path to package.xml file to check')
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument(
            '--dot', action='store_true', help='output DOT graph')
        parser.add_argument(
            '--target', default='python',
            help='Debian package to trace to (default python)')

    def do_command(self, args):
        all_paths = []
        tracer = PackageXMLTracer(quiet=args.quiet)

        try:
            all_paths = tracer.trace_paths(args.path, args.target)
        except OSError as e:
            sys.stderr.write(str(e) + '\n')
            return 2
        except KeyError:
            return 2

        if args.dot:
            edge_legend = {}
            edge_legend.update(APT_EDGE_LEGEND)
            edge_legend.update(ROSDEP_EDGE_LEGEND)
            edge_legend.update(PACKAGE_XML_EDGE_LEGEND)
            node_legend = {}
            node_legend.update(ROSDEP_NODE_LEGEND)
            node_legend.update(PACKAGE_XML_NODE_LEGEND)
            print(paths_to_dot(
                all_paths,
                edge_legend=edge_legend,
                node_legend=node_legend))
        elif not args.quiet:
            if all_paths:
                print('{} depends on {}'.format(args.path, args.target))
            else:
                print('{} does not depend on {}'.format(args.path, args.target))

        if all_paths:
            # non-zero exit code to indicate it does depend on target
            # because it's assumed depending on target is undesirable
            return 1
        return 0
