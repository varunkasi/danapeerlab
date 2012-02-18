#!/bin/sh

PYTHON27="/Library/Frameworks/Python.framework/Versions/2.7/bin/python-32"
PYTHON="/Library/Frameworks/Python.framework/Versions/current/bin/python"
RUN=""

# Determine script dir
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

if [ -e $PYTHON27 ]
then
  RUN=$PYTHON27
else
  RUN=$PYTHON
fi

if [ -e $RUN ]
then
  cd $SCRIPT_DIR
  cd ../Resources
  echo "Checking for updates..."
  svn checkout http://danapeerlab.googlecode.com/svn/trunk/freecell freecell
  cd freecell/src
  if [ -e main.py ]
  then
    $RUN main.py
  else
    echo "Freecell was not loaded, make sure you are connected to the internet and try again."
  fi
else
  echo "I can't find Python. Please install it from http://python.org/ftp/python/2.7.2/python-2.7.2-macosx10.3.dmg"
fi
