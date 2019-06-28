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

import os
import sys

from .apt_tracer import APT_EDGE_LEGEND
from .apt_tracer import AptTracer
from .dependency_tracer import DependencyTracer
from .dot import paths_to_dot
from .rosdep import is_rosdep_initialized

from apt.cache import Cache
from catkin_pkg.package import parse_package


class PackageXMLTracer(DependecyTracer):

    def __init__(self, cache=None, quiet=True):
        if not cache:
            cache = Cache()
        self._cache = cache
        self._quiet = quiet

    def trace_paths(self, start: str, target: str):
        # start: path to a ROS package
        # target: name of a debian package

        self._visited_pkgs = []
        self._pkgs_to_target = set([])
        self._edges_to_target = []

        # TODO(sloretz) must recursively trace package.xml files here
        # because one package could depend on another package in the system
        # rospack can find them
        # each key can be a ros package or a rosdep key, and paths from both need to be merged
        # graph nodes should be rosdep: for rosdep keys and rospkg for ros packages
        # ros packages will need a legend for each type of dependency
        pass
        # TODO(sloretz) return list of 3-tuples (start: str, end: str, type: str)

    def _trace_path(self, start, target):
        """return true if path leads to target"""
        if start.name in self._visited_pkgs:
            return start.name in self._pkgs_to_target

        # TODO(sloretz) for each dep, is it a package or rosdep key?


PACKAGE_XML_EDGE_LEGEND = {
  'build_depend': '[color=pink]',
  'buildtool_depend': '[color=pink]',
  'build_export_depend': '[color=pink]',
  'buildtool_export_depend': '[color=pink]',
  'exec_depend': '[color=pink]',
  'test_depend': '[color=pink]',
  'doc_depend': '[color=pink]',
}


class CheckPackageXMLCommand:
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
        # TODO option to output just the rosdep keys that depend on python

    def do_command(self, args):
        if not is_rosdep_initialized():
            sys.stderr.write(
                'The rosdep database is not ready to be used. '
                'Run \n\n\trosdep resolve {}\n\n'
                'for instructions on how to fix this.\n'.format(
                    args.key))
            return 2

        all_paths = []

        try:
            package = parse_package(args.path)
        except OSError as e:
            sys.stderr.write(str(e) + '\n')
            return 2

        # print(package)
        print(package.build_depends)
        print(package.buildtool_depends)
        print(package.build_export_depends)
        print(package.buildtool_export_depends)
        print(package.exec_depends)
        print(package.test_depends)
        print(package.doc_depends)
        # print(package.group_depends)  # Are these evaluated?

        # for each type of dependency
        #   what kind of package is it?
        #       is it a rosdep key?
        #       Is it a ros package?
        #           I think I need to use rospack to determine this
        #           rospack find <package>
        #           Also this ros workspace needs to be sourced
        print(package.build_depends[0].name)

        if all_paths:
            # non-zero exit code to indicate it does depend on target
            # because it's assumed depending on target is undesirable
            return 1
        return 0
