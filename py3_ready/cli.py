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

import sys
import argparse


def please_install(module, debian_package_suffix):
    sys.exit("""Unable to import {module}. Please install it on this system.

        sudo apt-get install python{version}-{suffix}""".format(
            module=module, version= sys.version_info.major,
            suffix=debian_package_suffix))


def main():

    try:
        import apt
    except ImportError:
        please_install('apt', 'apt')
    from .apt_tracer import AptTracerCommand

    try:
        import rosdep2
    except ImportError:
        please_install('rosdep2', 'rosdep-modules')
    from .rosdep import CheckRosdepCommand

    try:
        import catkin_pkg
    except ImportError:
        please_install('catkin_pkg', 'catkin-pkg-modules')
    from .package_xml import CheckPackageCommand

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    cmd_classes = [
        AptTracerCommand,
        CheckRosdepCommand,
        CheckPackageCommand
    ]

    for cmd_class in cmd_classes:
        sub_parser = subparsers.add_parser(
            cmd_class.COMMAND_NAME, help=cmd_class.COMMAND_HELP)
        cmd = cmd_class(sub_parser)
        sub_parser.set_defaults(func=cmd.do_command)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_usage()
    else:
        sys.exit(args.func(args))
