=========
py3-ready
=========

This is a tool for checking if your ROS package or its dependencies depend on python 2.

Usage
^^^^^
All commands exit with code 1 if the package does depend on python 2, and 0 if does not.
If any unrecoverable error occurs then the exit code is 2.

check-package-xml
:::::::::::::::::

This uses **rospack**, **rosdep**, and **apt** to check if any dependency of a ROS package depends on python2.
The command takes a path to a `package.xml` file or directory containing one.
Use **--quiet** to suppress warnings and human readable output.

::


    $ py3-ready check-package-xml $(rospack find catkin)
    python-argparse did not resolve to an apt package
    /opt/ros/melodic/share/catkin depends on python

Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.

::

    $ py3-ready check-package-xml --quiet --dot $(rospack find genmsg)
    digraph G {
      "python-catkin-pkg" -> "python-pyparsing"[color=blue];  // Depends
      "pkg: genmsg" -> "pkg: catkin"[color=pink];  // buildtool_depend
      "python-pbr" -> "python-pkg-resources"[color=blue];  // Depends
      "pkg: genmsg" -> "rosdep: python-empy"[color=pink];  // exec_depend
      "pkg: genmsg" -> "pkg: catkin"[color=pink];  // exec_depend
      "pkg: genmsg" -> "rosdep: python-empy"[color=pink];  // build_export_depend
      "python-roman" -> "python:any"[color=blue];  // Depends
      "python-catkin-pkg-modules" -> "python-pyparsing"[color=blue];  // Depends
      "pkg: catkin" -> "rosdep: python-nose"[color=pink];  // test_depend
      "pkg: catkin" -> "rosdep: google-mock"[color=pink];  // build_export_depend
      "python-pbr" -> "python:any"[color=blue];  // Depends
      "python-nose" -> "python:any"[color=blue];  // Depends
      "pkg: catkin" -> "rosdep: python-mock"[color=pink];  // test_depend
      "pkg: genmsg" -> "pkg: catkin"[color=pink];  // build_export_depend
      "python-dateutil" -> "python:any"[color=blue];  // Depends
      "rosdep: python-nose" -> "python-nose"[color=orange];  // rosdep
      "pkg: catkin" -> "rosdep: python-catkin-pkg"[color=pink];  // exec_depend
      "python-empy" -> "python"[color=blue];  // Depends
      "python-funcsigs" -> "python:any"[color=blue];  // Depends
      "python-catkin-pkg-modules" -> "python:any"[color=blue];  // Depends
      "python-mock" -> "python-pbr"[color=blue];  // Depends
      "python-catkin-pkg" -> "python-dateutil"[color=blue];  // Depends
      "rosdep: google-mock" -> "google-mock"[color=orange];  // rosdep
      "python-nose" -> "python-pkg-resources"[color=blue];  // Depends
      "python-catkin-pkg" -> "python:any"[color=blue];  // Depends
      "pkg: catkin" -> "rosdep: python-catkin-pkg"[color=pink];  // build_export_depend
      "python-catkin-pkg-modules" -> "python-dateutil"[color=blue];  // Depends
      "python-catkin-pkg" -> "python-docutils"[color=blue];  // Depends
      "googletest" -> "python:any"[color=blue];  // Depends
      "rosdep: python-mock" -> "python-mock"[color=orange];  // rosdep
      "pkg: catkin" -> "rosdep: python-nose"[color=pink];  // build_export_depend
      "python-pkg-resources" -> "python:any"[color=blue];  // Depends
      "python-docutils" -> "python-roman"[color=blue];  // Depends
      "python-catkin-pkg" -> "python-catkin-pkg-modules"[color=blue];  // Depends
      "rosdep: gtest" -> "libgtest-dev"[color=orange];  // rosdep
      "python-six" -> "python:any"[color=blue];  // Depends
      "python-docutils" -> "python:any"[color=blue];  // Depends
      "python-catkin-pkg-modules" -> "python-docutils"[color=blue];  // Depends
      "python-mock" -> "python-six"[color=blue];  // Depends
      "rosdep: python-catkin-pkg" -> "python-catkin-pkg"[color=orange];  // rosdep
      "pkg: catkin" -> "rosdep: gtest"[color=pink];  // build_export_depend
      "python-mock" -> "python:any"[color=blue];  // Depends
      "pkg: catkin" -> "rosdep: python-catkin-pkg"[color=pink];  // build_depend
      "pkg: catkin" -> "rosdep: python-empy"[color=pink];  // build_depend
      "rosdep: python-empy" -> "python-empy"[color=orange];  // rosdep
      "python-empy" -> "python:any"[color=blue];  // Depends
      "python-pyparsing" -> "python:any"[color=blue];  // Depends
      "google-mock" -> "googletest"[color=blue];  // Depends
      "python-dateutil" -> "python-six"[color=blue];  // Depends
      "python-pbr" -> "python-six"[color=blue];  // Depends
      "python:any" -> "python"[color=green];  // virtual
      "pkg: catkin" -> "rosdep: python-empy"[color=pink];  // build_export_depend
      "libgtest-dev" -> "googletest"[color=blue];  // Depends
      "python-mock" -> "python-funcsigs"[color=blue];  // Depends
    }

By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.

::

    $ py3-ready check-package-xml --target python3 $(rospack find gazebo_ros) 2>/dev/null
    /opt/ros/melodic/share/gazebo_ros depends on python3

check-rosdep
::::::::::::

This uses **rosdep** and **apt** to check if a rosdep key recursively depends on python 2.

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
