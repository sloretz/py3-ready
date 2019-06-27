=========
py3-ready
=========

This is a tool for checking if your ROS package or its dependencies depend on python 2.

Usage
^^^^^
check-rosdep
:::::::::

This uses **rosdep** and **apt** to check if a rosdep key recursively depends on python 2.
It exits with code 1 if the package does depend on python 2, otherwise the exit code is 0.

::

    $ py3-ready check-rosdep python-sip
    rosdep key python-sip depends on python

Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.
Use **--quiet** to suppress warnings and human readable output.

::

    $ py3-ready check-rosdep --quiet --dot boost
    digraph G {
      "libboost-mpi-python1.65-dev" -> "libboost-mpi-python1.65.1"[color=blue];  // Depends
      "libboost-mpi-python1.65.1" -> "python:any"[color=blue];  // Depends
      "libboost-mpi-python1.65.1" -> "python"[color=blue];  // Depends
      "libboost-all-dev" -> "libboost-mpi-python-dev"[color=blue];  // Depends
      "libboost-python1.65-dev" -> "python-dev"[color=blue];  // Depends
      "python-dev" -> "python"[color=blue];  // Depends
      "libboost-mpi-python-dev" -> "libboost-mpi-python1.65-dev"[color=blue];  // Depends
      "boost" -> "libboost-all-dev"[color=orange];  // rosdep
      "python:any" -> "python"[color=green];  // virtual
      "libboost-all-dev" -> "libboost-python-dev"[color=blue];  // Depends
      "libboost-python-dev" -> "libboost-python1.65-dev"[color=blue];  // Depends
    }

By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.


::

    $ py3-ready check-rosdep --target python3 python-sip
    rosdep key python-sip does not depend on python3

check-apt
:::::::::

This uses **apt** to check if a debian package recursively depends on python 2.
It exits with code 1 if the package does depend on python 2, otherwise the exit code is 0.

::

    $ py3-ready check-apt libboost-python-dev
    libboost-python-dev depends on python


Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.
Use **--quiet** to suppress warnings and human readable output.

::

    $ py3-ready check-apt --dot --quiet libboost-all-dev
    digraph G {
      "libboost-mpi-python1.65.1" -> "python:any"[color=blue];  // Depends
      "libboost-mpi-python1.65-dev" -> "libboost-mpi-python1.65.1"[color=blue];  // Depends
      "libboost-python1.65-dev" -> "python-dev"[color=blue];  // Depends
      "libboost-all-dev" -> "libboost-mpi-python-dev"[color=blue];  // Depends
      "libboost-all-dev" -> "libboost-python-dev"[color=blue];  // Depends
      "libboost-python-dev" -> "libboost-python1.65-dev"[color=blue];  // Depends
      "python:any" -> "python"[color=green];  // virtual
      "libboost-mpi-python1.65.1" -> "python"[color=blue];  // Depends
      "python-dev" -> "python"[color=blue];  // Depends
      "libboost-mpi-python-dev" -> "libboost-mpi-python1.65-dev"[color=blue];  // Depends
    }

By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.


::

    $ py3-ready check-apt --target python3 python3-apt
    python3-apt depends on python3
