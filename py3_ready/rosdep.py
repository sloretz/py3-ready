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

"""Tools for checking dependencies of rosdep packages."""

from __future__ import print_function

import os
import sys

from .apt_tracer import APT_EDGE_LEGEND
from .apt_tracer import AptTracer
from .dot import paths_to_dot

from apt.cache import Cache
from rosdep2 import create_default_installer_context
from rosdep2 import get_default_installer
from rosdep2.lookup import RosdepLookup
from rosdep2.platforms.debian import AptInstaller
from rosdep2.rospkg_loader import DEFAULT_VIEW_KEY
from rosdep2.sources_list import CACHE_INDEX
from rosdep2.sources_list import get_sources_cache_dir
from rosdep2.sources_list import get_sources_list_dir
from rosdep2.sources_list import SourcesListLoader


def is_rosdep_initialized():
    sources_cache_dir = get_sources_cache_dir()
    filename = os.path.join(sources_cache_dir, CACHE_INDEX)
    if os.path.exists(filename):
        return True
    else:
        return False

    sources_list_dir = get_sources_list_dir()
    if not os.path.exists(sources_list_dir):
        return False
    else:
        filelist = [f for f in os.listdir(sources_list_dir) if f.endswith('.list')]
        if not filelist:
            return False
    return True


def resolve_rosdep_key(key, quiet=False):
    sources_loader = SourcesListLoader.create_default(
        sources_cache_dir=get_sources_cache_dir(),
        os_override=None,
        verbose=False)
    lookup = RosdepLookup.create_from_rospkg(sources_loader=sources_loader)
    lookup.verbose = False

    installer_context = create_default_installer_context(verbose=False)

    installer, installer_keys, default_key, \
        os_name, os_version = get_default_installer(
            installer_context=installer_context,
            verbose=False)

    view = lookup.get_rosdep_view(DEFAULT_VIEW_KEY, verbose=False)
    try:
        d = view.lookup(key)
    except KeyError as e:
        sys.stderr.write('Invalid key "{}": {}\n'.format(key, e))
        return

    rule_installer, rule = d.get_rule_for_platform(
        os_name, os_version, installer_keys, default_key)

    installer = installer_context.get_installer(rule_installer)
    resolved = installer.resolve(rule)

    for error in lookup.get_errors():
        if not quiet:
            print('WARNING: %s' % (error), file=sys.stderr)

    return {installer: resolved}


ROSDEP_EDGE_LEGEND = {
    'rosdep': '[color=orange]',
}


class CheckRosdepCommand:
    COMMAND_NAME='check-rosdep'
    COMMAND_HELP='check if rosdep key depends on python 2'

    def __init__(self, parser):
        # arguments for key, quiet, and dot output
        parser.add_argument(
            'key', type=str,
            help='rosdep key to check for dependency on python 2')
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument(
            '--dot', action='store_true', help='output DOT graph')
        parser.add_argument(
            '--target', default='python',
            help='Debian package to trace to (default python)')

    def do_command(self, args):
        if not is_rosdep_initialized():
            sys.stderr.write(
                'The rosdep database is not ready to be used. '
                'Run \n\n\trosdep resolve {}\n\n'
                'for instructions on how to fix this.\n'.format(
                    args.key))
            return 2

        resolved = resolve_rosdep_key(args.key)
        if resolved is None:
            return 2

        apt_depends = []

        for installer, pkgs in resolved.items():
            if isinstance(installer, AptInstaller):
                apt_depends = pkgs

        target = args.target

        if not apt_depends:
            if not args.quiet:
                print('{} might not depend on {}'.format(apt.key, target))

        all_paths = []
        cache = Cache()

        for apt_depend in apt_depends:
            tracer = AptTracer(quiet=args.quiet)

            try:
                paths = tracer.trace_paths(apt_depend, target)
            except KeyError:
                return 2

            if paths:
                start_pkg = None
                for edge in paths:
                    if edge[1] is None:
                        start_pkg = edge[0]
                        break
                first_edge = (
                    'rosdep: ' + args.key,
                    start_pkg,
                    'rosdep'
                )
                paths.append(first_edge)
                all_paths.extend(paths)

        if args.dot:
            legend = {}
            legend.update(APT_EDGE_LEGEND)
            legend.update(ROSDEP_EDGE_LEGEND)
            print(paths_to_dot(list(set(all_paths)), edge_legend=legend))
        elif not args.quiet:
            if all_paths:
                print('rosdep key {} depends on {}'.format(args.key, target))
            else:
                # TODO
                print('rosdep key {} does not depend on {}'.format(args.key, target))

        if all_paths:
            # non-zero exit code to indicate it does depend on target
            # because it's assumed depending on target is undesirable
            return 1
        return 0
