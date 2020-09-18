=========
py3-ready
=========

This is a tool for checking if your ROS package or its dependencies depend on python 2.

Install
^^^^^^^

This package works on Ubuntu and Debian, and it needs some packages installed on the system.

Install these if the default ``python`` is Python 2 (Ubuntu Bionic, Debian Stretch, etc).

::

    $ sudo apt-get install python-apt
    $ sudo apt-get install python-rosdep-modules
    $ sudo apt-get install python-catkin-pkg-modules

Install these if the default ``python`` is Python 3 (Ubuntu  focal, Debian Buster, etc).

::

    $ sudo apt-get install python3-apt
    $ sudo apt-get install python3-rosdep-modules
    $ sudo apt-get install python3-catkin-pkg-modules


Then install from PyPI.org.

::

    $ pip install py3-ready

If you would like to install from source then create a virtual environment with access to system packages.

::

    $ cd py3-ready/
    # Set up Python 2 virtual environment
    $ virtualenv --system-site-packages ssenv2
    $ . ssenv2/bin/activate
    $ python setup.py develop
    $ deactivate
    # Set up Python 3 virtual environment
    $ python3 venv --system-site-packages ssenv3
    $ . ssenv3/bin/activate
    $ python setup.py develop


Usage
^^^^^
All commands exit with code 1 if the package does depend on python 2, and 0 if does not.
If any unrecoverable error occurs then the exit code is 2.

check-package
:::::::::::::::::

This checks if any dependency of a ROS package depends on python2.
The command takes a name of a ROS package.
The package must exist in a sourced workspace.
Use **--quiet** to suppress warnings and human readable output.

::

    $ py3-ready check-package catkin
    python-argparse did not resolve to an apt package
    /opt/ros/melodic/share/catkin depends on python

Passing **--dot** outputs the dependency graph in `DOT <https://www.graphviz.org/doc/info/lang.html>`_ format.

::

    $ py3-ready check-package --quiet --dot catkin
    digraph G {
      "catkin%package" -> "python-empy%rosdep"[color=pink];  // build_export_depend
      "python-empy%rosdep" -> "python-empy%apt"[color=orange];  // rosdep
      "python-catkin-pkg%rosdep" -> "python-catkin-pkg%apt"[color=orange];  // rosdep
      "catkin%package" -> "python-mock%rosdep"[color=pink];  // test_depend
      "python-mock%apt" -> "python-funcsigs%apt"[color=blue];  // Depends
      "python:any%apt" -> "python%apt"[color=green];  // virtual
      "python-pbr%apt" -> "python-six%apt"[color=blue];  // Depends
      "google-mock%apt" -> "googletest%apt"[color=blue];  // Depends
      "python-mock%apt" -> "python-pbr%apt"[color=blue];  // Depends
      "python-pbr%apt" -> "python-pkg-resources%apt"[color=blue];  // Depends
      "python-nose%apt" -> "python-pkg-resources%apt"[color=blue];  // Depends
      "catkin%package" -> "python-empy%rosdep"[color=pink];  // build_depend
      "python-docutils%apt" -> "python:any%apt"[color=blue];  // Depends
      "catkin%package" -> "python-catkin-pkg%rosdep"[color=pink];  // build_export_depend
      "python-dateutil%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-nose%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-funcsigs%apt" -> "python:any%apt"[color=blue];  // Depends
      "gtest%rosdep" -> "libgtest-dev%apt"[color=orange];  // rosdep
      "python-catkin-pkg%apt" -> "python-docutils%apt"[color=blue];  // Depends
      "catkin%package" -> "python-catkin-pkg%rosdep"[color=pink];  // build_depend
      "python-docutils%apt" -> "python-roman%apt"[color=blue];  // Depends
      "python-mock%rosdep" -> "python-mock%apt"[color=orange];  // rosdep
      "python-nose%rosdep" -> "python-nose%apt"[color=orange];  // rosdep
      "google-mock%rosdep" -> "google-mock%apt"[color=orange];  // rosdep
      "catkin%package" -> "python-catkin-pkg%rosdep"[color=pink];  // exec_depend
      "python-catkin-pkg-modules%apt" -> "python-pyparsing%apt"[color=blue];  // Depends
      "catkin%package" -> "gtest%rosdep"[color=pink];  // build_export_depend
      "catkin%package" -> "python-nose%rosdep"[color=pink];  // build_export_depend
      "python-six%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-dateutil%apt" -> "python-six%apt"[color=blue];  // Depends
      "python-catkin-pkg%apt" -> "python-pyparsing%apt"[color=blue];  // Depends
      "python-catkin-pkg-modules%apt" -> "python-docutils%apt"[color=blue];  // Depends
      "python-pbr%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-pyparsing%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-catkin-pkg%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-catkin-pkg-modules%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-mock%apt" -> "python-six%apt"[color=blue];  // Depends
      "catkin%package" -> "python-nose%rosdep"[color=pink];  // test_depend
      "python-empy%apt" -> "python%apt"[color=blue];  // Depends
      "python-mock%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-catkin-pkg%apt" -> "python-dateutil%apt"[color=blue];  // Depends
      "python-catkin-pkg%apt" -> "python-catkin-pkg-modules%apt"[color=blue];  // Depends
      "googletest%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-empy%apt" -> "python:any%apt"[color=blue];  // Depends
      "catkin%package" -> "google-mock%rosdep"[color=pink];  // build_export_depend
      "python-catkin-pkg-modules%apt" -> "python-dateutil%apt"[color=blue];  // Depends
      "libgtest-dev%apt" -> "googletest%apt"[color=blue];  // Depends
      "python-pkg-resources%apt" -> "python:any%apt"[color=blue];  // Depends
      "python-roman%apt" -> "python:any%apt"[color=blue];  // Depends
    
      "python-mock%rosdep"[color=orange,shape=rect][label="python-mock"];  // rosdep
      "python-mock%apt"[label="python-mock"];  // apt
      "python-catkin-pkg-modules%apt"[label="python-catkin-pkg-modules"];  // apt
      "python-pyparsing%apt"[label="python-pyparsing"];  // apt
      "python-catkin-pkg%apt"[label="python-catkin-pkg"];  // apt
      "gtest%rosdep"[color=orange,shape=rect][label="gtest"];  // rosdep
      "python:any%apt"[label="python:any"];  // apt
      "python-dateutil%apt"[label="python-dateutil"];  // apt
      "python-roman%apt"[label="python-roman"];  // apt
      "catkin%package"[color=pink,shape=hexagon][label="catkin"];  // package
      "python-empy%apt"[label="python-empy"];  // apt
      "google-mock%apt"[label="google-mock"];  // apt
      "python-nose%rosdep"[color=orange,shape=rect][label="python-nose"];  // rosdep
      "python-pbr%apt"[label="python-pbr"];  // apt
      "python-pkg-resources%apt"[label="python-pkg-resources"];  // apt
      "python-funcsigs%apt"[label="python-funcsigs"];  // apt
      "python-nose%apt"[label="python-nose"];  // apt
      "python%apt"[label="python"];  // apt
      "google-mock%rosdep"[color=orange,shape=rect][label="google-mock"];  // rosdep
      "python-empy%rosdep"[color=orange,shape=rect][label="python-empy"];  // rosdep
      "python-catkin-pkg%rosdep"[color=orange,shape=rect][label="python-catkin-pkg"];  // rosdep
      "libgtest-dev%apt"[label="libgtest-dev"];  // apt
      "googletest%apt"[label="googletest"];  // apt
      "python-docutils%apt"[label="python-docutils"];  // apt
      "python-six%apt"[label="python-six"];  // apt
    }

By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.

::

    $ py3-ready check-package --target python3 gazebo_ros 2>/dev/null
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
      "libboost-mpi-python1.65-dev%apt" -> "libboost-mpi-python1.65.1%apt"[color=blue];  // Depends
      "libboost-mpi-python1.65.1%apt" -> "python%apt"[color=blue];  // Depends
      "libboost-all-dev%apt" -> "libboost-mpi-python-dev%apt"[color=blue];  // Depends
      "libboost-mpi-python-dev%apt" -> "libboost-mpi-python1.65-dev%apt"[color=blue];  // Depends
      "libboost-python1.65-dev%apt" -> "python-dev%apt"[color=blue];  // Depends
      "libboost-mpi-python1.65.1%apt" -> "python:any%apt"[color=blue];  // Depends
      "python:any%apt" -> "python%apt"[color=green];  // virtual
      "libboost-python-dev%apt" -> "libboost-python1.65-dev%apt"[color=blue];  // Depends
      "boost%rosdep" -> "libboost-all-dev%apt"[color=orange];  // rosdep
      "python-dev%apt" -> "python%apt"[color=blue];  // Depends
      "libboost-all-dev%apt" -> "libboost-python-dev%apt"[color=blue];  // Depend
      "python%apt"[label="python"];  // apt
    
      "libboost-mpi-python-dev%apt"[label="libboost-mpi-python-dev"];  // apt
      "boost%rosdep"[color=orange,shape=rect][label="boost"];  // rosdep
      "libboost-python-dev%apt"[label="libboost-python-dev"];  // apt
      "libboost-mpi-python1.65-dev%apt"[label="libboost-mpi-python1.65-dev"];  // apt
      "libboost-python1.65-dev%apt"[label="libboost-python1.65-dev"];  // apt
      "libboost-mpi-python1.65.1%apt"[label="libboost-mpi-python1.65.1"];  // apt
      "python-dev%apt"[label="python-dev"];  // apt
      "python:any%apt"[label="python:any"];  // apt
      "libboost-all-dev%apt"[label="libboost-all-dev"];  // apt
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
      "libboost-mpi-python1.65.1%apt" -> "python:any%apt"[color=blue];  // Depends
      "libboost-all-dev%apt" -> "libboost-python-dev%apt"[color=blue];  // Depends
      "libboost-python-dev%apt" -> "libboost-python1.65-dev%apt"[color=blue];  // Depends
      "libboost-python1.65-dev%apt" -> "python-dev%apt"[color=blue];  // Depends
      "python-dev%apt" -> "python%apt"[color=blue];  // Depends
      "libboost-all-dev%apt" -> "libboost-mpi-python-dev%apt"[color=blue];  // Depends
      "libboost-mpi-python1.65-dev%apt" -> "libboost-mpi-python1.65.1%apt"[color=blue];  // Depends
      "libboost-mpi-python1.65.1%apt" -> "python%apt"[color=blue];  // Depends
      "python:any%apt" -> "python%apt"[color=green];  // virtual
      "libboost-mpi-python-dev%apt" -> "libboost-mpi-python1.65-dev%apt"[color=blue];  // Depends
    
      "libboost-python1.65-dev%apt"[label="libboost-python1.65-dev"];  // apt
      "python-dev%apt"[label="python-dev"];  // apt
      "python:any%apt"[label="python:any"];  // apt
      "python%apt"[label="python"];  // apt
      "libboost-mpi-python-dev%apt"[label="libboost-mpi-python-dev"];  // apt
      "libboost-mpi-python1.65-dev%apt"[label="libboost-mpi-python1.65-dev"];  // apt
      "libboost-python-dev%apt"[label="libboost-python-dev"];  // apt
      "libboost-all-dev%apt"[label="libboost-all-dev"];  // apt
      "libboost-mpi-python1.65.1%apt"[label="libboost-mpi-python1.65.1"];  // apt
    }


By default this looks for dependencies on the debian package named **python**.
Use **--target** to change this name.


::

    $ py3-ready check-apt --target python3 python3-apt
    python3-apt depends on python3
