#!/usr/bin/env python
import logging
import sys
from StringIO import StringIO
import random
import struct
import os
from collections import namedtuple
import numpy as np
from numpy import array
import biology.markers
from biology.markers import Markers
from biology.markers import marker_from_name
from biology.kdtree import KDTree
from biology.kdtree import Rectangle
from scriptservices import services
from biology.markers import normalize_markers
from autoreloader import AutoReloader

class RelationTable(AutoReloader):
  def __init__(self, data, dims):
    """Creates a new relation table. This class is immuteable.
    
    data -- a 2 dimension n x n array with the table data
    dims -- object that are associated with table's columns and rows.
    """
    self.data = data
    self.dims = dims
