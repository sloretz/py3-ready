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
from .dot import paths_to_dot
from .rosdep import is_rosdep_initialized
from .rosdep import ROSDEP_EDGE_LEGEND
from .rosdep import RosdepTracer

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
        self._tracer = RosdepTracer(cache=self._cache, quiet=self._quiet)

    def trace_paths(self, start, target):
        # start: path to a ROS package
        # target: name of a debian package
        start_pkg = parse_package(start)

        self._visited_pkgs = []
        self._pkgs_to_target = set([])
        self._visited_rosdeps = []
        self._rosdeps_to_target = set([])
        self._edges_to_target = []
        self._trace_path(start_pkg, target)
        return list(set(self._edges_to_target))

    def _trace_path(self, start, target):
        """return true if path leads to target debian package"""
        if start.name in self._visited_pkgs:
            return start.name in self._pkgs_to_target
        self._visited_pkgs.append(start.name)

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

        leads_to_target = False
        for dep, rawtype in depends:
            if dep.name in rosdep_keys:
                dep_leads_to_target = False
                if dep.name in self._visited_rosdeps:
                    if dep.name in self._rosdeps_to_target:
                        dep_leads_to_target = True
                else:
                    self._visited_rosdeps.append(dep.name)
                    # Trace rosdep key to target
                    rosdep_paths = self._tracer.trace_paths(dep.name, target)
                    if rosdep_paths:
                        dep_leads_to_target = True
                        self._edges_to_target.extend(rosdep_paths)
                        self._rosdeps_to_target.add(dep.name)
                if dep_leads_to_target:
                    leads_to_target = True
                    first_edge = (
                        'pkg: ' + start.name,
                        'rosdep: ' + dep.name,
                        rawtype
                    )
                    self._edges_to_target.append(first_edge)
                    self._pkgs_to_target.add(start.name)
                    leads_to_target = True
            else:
                pkg = parse_package(self._rospack.get_path(dep.name))
                if self._trace_path(pkg, target):
                    first_edge = (
                        'pkg: ' + start.name,
                        'pkg: ' + dep.name,
                        rawtype
                    )
                    self._edges_to_target.append(first_edge)
                    self._pkgs_to_target.add(start.name)
                    leads_to_target = True

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
            legend = {}
            legend.update(APT_EDGE_LEGEND)
            legend.update(ROSDEP_EDGE_LEGEND)
            legend.update(PACKAGE_XML_EDGE_LEGEND)
            print(paths_to_dot(all_paths, edge_legend=legend))
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
