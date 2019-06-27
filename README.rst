=========
py3-ready
=========

This is a tool for checking if your ROS package or its dependencies depend on python 2.

Usage
^^^^^

check-apt
:::::::::

This checks uses **apt** to check if a debian package recursively depends on python 2.
It exits with code 0 if the package does not depend on python2.
The exit code is 1 if it does depend on python.

::

    py3-ready check-apt libboost-python-dev

Passing **--dot** outputs the dependency graph in `DOT https://www.graphviz.org/doc/info/lang.html`_ format.

::
    py3-ready check-apt --dot libboost-all-dev


By default this looks for dependencies on the debian package named **python**.
Use **--target** to change which package to look for recursive dependency.

::
    py3-ready check-apt --target python3 libboost-all-dev

Use **--quiet** to suppress warnings and human readable output.

::

    py3-ready check-apt --quiet libboost-python-dev
