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

import copy
import sys

from .dependency_tracer import DependencyTracer
from .dot import paths_to_dot

from apt.cache import Cache
from apt.package import Package


class AptTracer(DependencyTracer):

    def __init__(self, cache=None, quiet=True):
        if not cache:
            cache = Cache()
        self._cache = cache
        self._quiet = quiet

    def trace_paths(self, start: str, target: str):
        start = self._cache.get(start)
        target = self._cache.get(target)
        self._visited_nodes = []
        self._nodes_to_target = set([])
        self._edges_to_target = []
        # Descend through dependency
        if self._trace_path(start, target):
            self._edges_to_target.append((start.name, None, None))
            self._nodes_to_target.add(start.name)
        # TODO(sloretz) why are edges sometimes repeated?
        return list(set(self._edges_to_target))

    def _trace_path(self, start, target):
        """Depth first search to trace paths to target."""
        if start.name in self._visited_nodes:
            return start.name in self._nodes_to_target
        self._visited_nodes.append(start.name)
        if start.name == target.name:
            # Found target, add path to paths
            return True
        if not start.candidate.dependencies:
            # lowest level and target not found
            return False
        leads_to_target = False
        for dependency in start.candidate.dependencies:
            rawtype = dependency.rawtype
            # Check all the candidates that can satisfy this dependency
            for base_dep in dependency:
                # Only walk upstream dependencies
                if base_dep.rawtype in ['Depends', 'PreDepends', 'Suggests', 'Recommends']:
                    if self._cache.is_virtual_package(base_dep.name):
                        for pkg in self._cache.get_providing_packages(base_dep.name):
                            if self._trace_path(pkg, target):
                                leads_to_target = True
                                edge1 = (start.name, base_dep.name, base_dep.rawtype)
                                edge2 = (base_dep.name, pkg.name, 'virtual')
                                self._edges_to_target.append(edge1)
                                self._edges_to_target.append(edge2)
                                self._nodes_to_target.add(base_dep.name)
                    else:
                        pkg = self._cache.get(base_dep.name)
                        if pkg is None:
                            if not self._quiet:
                                sys.stderr.write(
                                    "'{}' not in apt cache. Used by '{}' as '{}'\n".format(
                                        base_dep.name, start.name, dependency))
                            continue
                        if self._trace_path(pkg, target):
                            leads_to_target = True
                            edge = (start.name, pkg.name, base_dep.rawtype)
                            self._edges_to_target.append(edge)
                            self._nodes_to_target.add(base_dep.name)
        return leads_to_target


APT_EDGE_LEGEND = {
    'virtual': '[color=green]',
    'Depends': '[color=blue]',
    'PreDepends': '[color=blue]',
    'Suggests': '[color=yellow]',
    'Recommends': '[color=yellow]',
}


class AptTracerCommand:

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

        paths = tracer.trace_paths(start, target)
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
