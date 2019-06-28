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
from rospkg import RosPack
from rospkg.common import PACKAGE_FILE
from rospkg.common import MANIFEST_FILE
from rospkg.manifest import InvalidManifest
from rospkg.manifest import parse_manifest_file


def get_rospack_manifest(path, rospack):
    if path.endswith(PACKAGE_FILE):
        path = os.path.dirname(path)
    print(path)
    # TODO(sloretz) why does this raise with PACKAGE_FILE?
    return parse_manifest_file(path, MANIFEST_FILE, rospack=rospack)


def get_rosdeps(pkg, rospack):
    m = get_rospack_manifest(pkg.filename, rospack)
    rosdeps = m.rosdeps
    return [r.name for r in rosdeps]


class PackageXMLTracer(DependencyTracer):

    def __init__(self, cache=None, quiet=True):
        if not cache:
            cache = Cache()
        self._cache = cache
        self._quiet = quiet
        self._rospack = RosPack()

    def trace_paths(self, start, target):
        # start: path to a ROS package
        # target: name of a debian package
        start_pkg = parse_package(start)

        self._visited_pkgs = []
        self._pkgs_to_target = set([])
        self._edges_to_target = []
        # TODO(sloretz) must recursively trace package.xml files here
        # because one package could depend on another package in the system
        # rospack can find them
        # each key can be a ros package or a rosdep key, and paths from both need to be merged
        # graph nodes should be rosdep: for rosdep keys and rospkg for ros packages
        # ros packages will need a legend for each type of dependency
        if self._trace_path(start_pkg, target):
            self._edges_to_target.append((start, None, None))
            self._nodes_to_target.add(start)
        return list(set(self._edges_to_target))
        # TODO(sloretz) return list of 3-tuples (start: str, end: str, type: str)

    def _trace_path(self, start, target):
        """return true if path leads to target debian package"""
        if start.name in self._visited_pkgs:
            return start.name in self._pkgs_to_target

        rosdep_keys = get_rosdeps(start, self._rospack)

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

        for dep, rawtype in depends:
            if dep.name in rosdep_keys:
                print(dep.name, "is a rosdep key")
            else:
                print(dep.name, "is a ros package at", self._rospack.get_path(dep.name))

        return False

        # TODO(sloretz) for each dep, is it a package or rosdep key?
        # this is what `rospack rosdep0` does
        # if it's a rosdep key, ask rosdep to resolve it for us
        # then use AptTracer to get the apt dependencies for it
        # if it's a ros package then call _trace_path on it to do the same
        # if it returns true then we depend on py2 because the ros package does
        # too


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
        tracer = PackageXMLTracer(quiet=args.quiet)

        try:
            paths = tracer.trace_paths(args.path, args.target)
        except OSError as e:
            sys.stderr.write(str(e) + '\n')
            return 2
        except KeyError:
            return 2

        if all_paths:
            # non-zero exit code to indicate it does depend on target
            # because it's assumed depending on target is undesirable
            return 1
        return 0
