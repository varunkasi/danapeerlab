# How to Install Freecell #
## Mac OSX ##
1. Install (or make sure you have):
  * [Python2.7-32](http://python.org/ftp/python/2.7.2/python-2.7.2-macosx10.3.dmg) (When this is installed you can type in python2.7-32 from your terminal to run Python)
  * [Numpy](http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-py2.7-python.org-macosx10.3.dmg) for python 2.7, macosx10.3
  * [Scipy](http://sourceforge.net/projects/scipy/files/scipy/0.10.0/scipy-0.10.0-py2.7-python.org-macosx10.3.dmg) for python 2.7, macosx10.3
  * [Matplotlib](http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0-py2.7-python.org-macosx10.3.dmg) for python 2.7, macosx10.3

You also need to have Matlab installed.

If you don't have any of the above, the installer will alert you.

2. [Download the mac installer](http://danapeerlab.googlecode.com/files/Freecell_osx.zip), extract and copy Freecell.app to /Applications and run it. On the first time this downloads Freecell, so it might take a while.


In the future, you can run Freecell\_noupdate to run Freecell without checking for updates.

You can download an example data pack from the following address:

`http://dl.dropbox.com/u/7777470/freecell_data_[password].zip`

(replace `[password]` with password)

The files in the archive should be extracted to `/Applications/Freecell.app/Contents/Resources/data`. This package enables the Population Picker module.



## Windows XP/7 ##
1. You will need a subversion client. You can get one from [silksvn](http://www.sliksvn.com/en/download).

2. You will also need to install:
  * [Python2.7 (32 bit)](http://www.python.org/download/)
  * [Numpy](http://sourceforge.net/projects/numpy/files/) for python 2.7, win32
  * [Scipy](http://sourceforge.net/projects/scipy/files/) for python 2.7, win32
  * [Matplotlib](http://sourceforge.net/projects/matplotlib/files/) for python 2.7, win32
  * [Pywin32](http://sourceforge.net/projects/pywin32/files/) for python 2.7, win32

You also need to have Matlab installed.

3. Pick a directory on your machine, and run in that directory:
> `svn checkout http://danapeerlab.googlecode.com/svn/trunk/freecell freecell`
This will load freecell into the freecell directory.

4. go to `freecell/src` directory and then run `python main.py`