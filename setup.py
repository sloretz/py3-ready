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

from setuptools import setup

with open("README.rst", "r") as fin:
  long_description = fin.read()

setup(
    name='py3-ready',
    version='0.1.0',
    packages=['py3_ready'],
    entry_points={
        'console_scripts': [
            'py3-ready = py3_ready.cli:main',
	    ]
    },
    author='Shane Loretz',
    author_email='sloretz@openrobotics.org',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: Apache Software License'
    ],
    description='A tool to identify dependencies on python 2.',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license='Apache License 2.0',
    install_requires=[],  # TODO(sloretz) what to do if deps are debian packages?
)
