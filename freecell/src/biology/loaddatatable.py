import logging
import cPickle
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
from biology.markers import normalize_markers
from biology.datatable import DataTable

def get_num_events(filename):
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

    #logging.info("Parsing TEXT segment")
    # read TEXT portion
    fcs.seek(text_start)
    delimeter = fcs.read(1)
    # First byte of the text portion defines the delimeter
    #logging.info("delimeter:%s" % delimeter)
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
    #logging.info("Number of dimensions:%d" % num_dims)

    num_events = int(fcs_vars['$TOT'])
    return num_events

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

    #logging.info("Parsing TEXT segment")
    # read TEXT portion
    fcs.seek(text_start)
    delimeter = fcs.read(1)
    # First byte of the text portion defines the delimeter
    #logging.info("delimeter:%s" % delimeter)
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
    #logging.info("Number of dimensions:%d" % num_dims)

    num_events = int(fcs_vars['$TOT'])
    #logging.info("Number of events:%d" % num_events)

    # Read DATA portion
    fcs.seek(data_start)
    #print "# of Data bytes",data_end-data_start+1
    data = fcs.read(data_end-data_start+1)

  #Determine data format
  #for key in fcs_vars.keys():
  #  print '%s:\t\t\t%s' % (key, fcs_vars[key])
  is_peng = False
  if fcs_vars.get('$COM', None) == 'PengQiu FCS writer':
    is_peng = True
    # fix peng bugs:
    datatype = 'f'
    endian = '>'
    fcs_vars['$CREATOR'] = fcs_vars['CREATOR']
    fcs_vars['$FCSversion'] = fcs_vars['FCSversion']
    fcs_vars['$FILENAME'] = fcs_vars['FILENAME']   
    #print [k for k in fcs_vars.keys() if k[0]!='$']
    #fcs_vars['$data'] = fcs_vars['temp']
    #del fcs_vars['temp']
    del fcs_vars['CREATOR']
    del fcs_vars['FCSversion']
    del fcs_vars['FILENAME']
    for key,val in fcs_vars.items():
      if val == 'GUID':
        del fcs_vars[key]
        fcs_vars['$GUID'] = key
      elif not key.startswith('$'):
        if not val.startswith('$'):
          #logging.warning('***' + key +':' + val)
          continue
        del fcs_vars[key]
        fcs_vars[val] = key
        
    
  else:
    datatype = fcs_vars['$DATATYPE']
    if datatype == 'F':
        datatype = 'f' # set proper data mode for struct module
        #logging.info("Data stored as single-precision (32-bit) floating point numbers")
    elif datatype == 'D':
        datatype = 'd' # set proper data mode for struct module
        #logging.info("Data stored as double-precision (64-bit) floating point numbers")
    else:
        assert False,"Error: Unrecognized $DATATYPE '%s'" % datatype
    
    # Determine endianess
    endian = fcs_vars['$BYTEORD']
    if endian == "4,3,2,1":
        endian = ">" # set proper data mode for struct module
        #print "Big endian data format"
    elif endian == "1,2,3,4":
        #print "Little endian data format"
        endian = "<" # set proper data mode for struct module
    else:
        assert False,"Error: This script can only read data encoded with $BYTEORD = 1,2,3,4 or 4,3,2,1"

  # Put data in StringIO so we can read bytes like a file    
  data = StringIO(data)

  #logging.info("Parsing DATA segment")
  # Create format string based on endianeness and the specified data type
  format = endian + str(num_dims) + datatype
  datasize = struct.calcsize(format)
  #logging.info("Data format:%s" % format)
  #logging.info("Data size:%d" % datasize)
  events = []
  # Read and unpack all the events from the data
  for e in range(num_events):
      event = struct.unpack(format,data.read(datasize))
      events.append(event)
  return fcs_vars,events,is_peng

load_data_table_CACHE = {}
def load_data_table(filename, extra_dims=[], extra_vals=[], extra_legends=[], arcsin_factor=1):
  global load_data_table_CACHE
  if not filename:
    raise Exception('No filename was provided to load_data_table')
  if not (filename, arcsin_factor)  in load_data_table_CACHE:
    fcs_vars, events, is_peng = fcsextract(filename)
    if not events:
      logging.error('File %s is empty' % filename)
      return None
    num_dims = len(events[0])
    #if is_peng:
    #  dim_names = [fcs_vars["$P%dR"%(i+1)] for i in xrange(num_dims)]
    #  print dim_names
    #else:
    print '\n'.join([str(x) for x in sorted(fcs_vars.items())])
    dim_names = []
    for i in xrange(num_dims):
      keys_to_try = ["$P%dS" % (i+1), "$P%dN"%(i+1)]
      keys_found = [key in fcs_vars for key in keys_to_try]
      if True in keys_found:
        dim_names.append(fcs_vars[keys_to_try[keys_found.index(True)]])
      else:
        dim_names.append('dim%d' % i+1)
    #print dim_names
    #print fcs_vars
    dims = [marker_from_name(name) for name in dim_names]
    dim_names = [str(dim) for dim in dims]
    data = array(events)
    indices_to_transform = [i for i,n in enumerate(dims) if n and n.needs_transform]
    #data[:,indices_to_transform] = np.arcsinh(data[:,indices_to_transform] / 5)
    data[:,indices_to_transform] = np.arcsinh(data[:,indices_to_transform] * arcsin_factor)
    
    # add extra dims, data:
    legends = [None] * len(dim_names) + extra_legends
    dim_names += extra_dims
    extra_vals_arr = np.array([extra_vals])
    extra_vals_arr = np.repeat(extra_vals_arr, data.shape[0], axis=0)
    data = np.append(data, extra_vals_arr, axis=1)    
    load_data_table_CACHE[(filename, arcsin_factor)] = biology.datatable.DataTable(data, dim_names, legends)
    logging.info('Loaded %d cells from file %s' % (load_data_table_CACHE[(filename, arcsin_factor)].data.shape[0], filename[:30]))
  return load_data_table_CACHE[(filename, arcsin_factor)]
