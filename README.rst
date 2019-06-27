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

    $ py3-ready check-apt libboost-python-dev
    libboost-python-dev depends on python


Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.

::

    $ py3-ready check-apt --dot libboost-all-dev
    'kldutils' not in apt cache. Used by 'dkms' as 'Depends: kmod | kldutils'
    'xorg-video-abi-11' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-12' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-13' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-14' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-15' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-18' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-19' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    'xorg-video-abi-20' not in apt cache. Used by 'nvidia-340' as 'Depends: xorg-video-abi-11 | xorg-video-abi-12 | xorg-video-abi-13 | xorg-video-abi-14 | xorg-video-abi-15 | xorg-video-abi-18 | xorg-video-abi-19 | xorg-video-abi-20 | xorg-video-abi-23 | xorg-video-abi-24'
    digraph G {
      "libboost-mpi-python1.65.1" -> "python"[color=blue];  // Depends
      "libboost-python1.65-dev" -> "python-dev"[color=blue];  // Depends
      "python-dev" -> "python"[color=blue];  // Depends
      "python:any" -> "python"[color=green];  // virtual
      "libboost-mpi-python-dev" -> "libboost-mpi-python1.65-dev"[color=blue];  // Depends
      "libboost-mpi-python1.65.1" -> "python:any"[color=blue];  // Depends
      "libboost-all-dev" -> "libboost-python-dev"[color=blue];  // Depends
      "libboost-all-dev" -> "libboost-mpi-python-dev"[color=blue];  // Depends
      "libboost-python-dev" -> "libboost-python1.65-dev"[color=blue];  // Depends
      "libboost-mpi-python1.65-dev" -> "libboost-mpi-python1.65.1"[color=blue];  // Depends
    }



By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.


::

    $ py3-ready check-apt --target python3 python3-apt     
    python3-apt depends on python3

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
