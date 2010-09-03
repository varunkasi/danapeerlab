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
from scriptservices import services
from biology.markers import normalize_markers
import biology.datatable

def fcsextract(filename):
  """Extracts data from an fcs file. 
  
  based on code from
  http://cyberaide.googlecode.com/svn/trunk/project/biostatistics/scripts/fcsextract.py
  """
  fcs_file_name = filename

  fcs = open(fcs_file_name,'rb')
  with fcs:
    header = fcs.read(58)
    version = header[0:6].strip()
    text_start = int(header[10:18].strip())
    text_end = int(header[18:26].strip())
    data_start = int(header[26:34].strip())
    data_end = int(header[34:42].strip())
    analysis_start = int(header[42:50].strip())
    analysis_end = int(header[50:58].strip())

    logging.info("Parsing TEXT segment")
    # read TEXT portion
    fcs.seek(text_start)
    delimeter = fcs.read(1)
    # First byte of the text portion defines the delimeter
    logging.info("delimeter:%s" % delimeter)
    text = fcs.read(text_end-text_start+1)

    #Variables in TEXT poriton are stored "key/value/key/value/key/value"
    keyvalarray = text.split(delimeter)
    fcs_vars = {}
    fcs_var_list = []
    # Iterate over every 2 consecutive elements of the array
    for k,v in zip(keyvalarray[::2],keyvalarray[1::2]):
        fcs_vars[k] = v
        fcs_var_list.append((k,v)) # Keep a list around so we can print them in order

    #from pprint import pprint; pprint(fcs_var_list)
    if data_start == 0 and data_end == 0:
        data_start = int(fcs_vars['$DATASTART'])
        data_end = int(fcs_vars['$DATAEND'])

    num_dims = int(fcs_vars['$PAR'])
    logging.info("Number of dimensions:%d" % num_dims)

    num_events = int(fcs_vars['$TOT'])
    logging.info("Number of events:%d" % num_events)

    # Read DATA portion
    fcs.seek(data_start)
    #print "# of Data bytes",data_end-data_start+1
    data = fcs.read(data_end-data_start+1)

  # Determine data format
  datatype = fcs_vars['$DATATYPE']
  if datatype == 'F':
      datatype = 'f' # set proper data mode for struct module
      logging.info("Data stored as single-precision (32-bit) floating point numbers")
  elif datatype == 'D':
      datatype = 'd' # set proper data mode for struct module
      logging.info("Data stored as double-precision (64-bit) floating point numbers")
  else:
      assert False,"Error: Unrecognized $DATATYPE '%s'" % datatype
  
  # Determine endianess
  endian = fcs_vars['$BYTEORD']
  if endian == "4,3,2,1":
      endian = ">" # set proper data mode for struct module
      print "Big endian data format"
  elif endian == "1,2,3,4":
      print "Little endian data format"
      endian = "<" # set proper data mode for struct module
  else:
      assert False,"Error: This script can only read data encoded with $BYTEORD = 1,2,3,4 or 4,3,2,1"

  # Put data in StringIO so we can read bytes like a file    
  data = StringIO(data)

  logging.info("Parsing DATA segment")
  # Create format string based on endianeness and the specified data type
  format = endian + str(num_dims) + datatype
  datasize = struct.calcsize(format)
  logging.info("Data format:%s" % format)
  logging.info("Data size:%d" % datasize)
  events = []
  # Read and unpack all the events from the data
  for e in range(num_events):
      event = struct.unpack(format,data.read(datasize))
      events.append(event)
  return fcs_vars,events

load_data_table_CACHE = {}
def load_data_table(filename):
  global load_data_table_CACHE
  if not filename in load_data_table_CACHE:
    fcs_vars, events = fcsextract(filename)
    if not events:
      raise Exception('empty file')
    num_dims = len(events[0])

    dim_names = [fcs_vars["$P%dS"%(i+1)] for i in xrange(num_dims)]
    dims = [marker_from_name(name) for name in dim_names]
    data = array(events)
    indices_to_transform = [i for i,n in enumerate(dims) if n.needs_transform]
    data[:,indices_to_transform] = np.arcsinh(data[:,indices_to_transform])
    load_data_table_CACHE[filename] = biology.datatable.DataTable(data, dim_names)
  return load_data_table_CACHE[filename]

