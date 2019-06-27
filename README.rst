=========
py3-ready
=========

This is a tool for checking if your ROS package or its dependencies depend on python 2.

Usage
^^^^^

check-apt
:::::::::

This uses **apt** to check if a debian package recursively depends on python 2.
It exits with code 1 if the package does depend on python 2, otherwise the exit code is 0.

::

    py3-ready check-apt libboost-python-dev

Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.

::

    py3-ready check-apt --dot libboost-all-dev


By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.

::

    py3-ready check-apt --target python3 libboost-all-dev

Use **--quiet** to suppress warnings and human readable output.

::

    py3-ready check-apt --quiet libboost-python-dev
