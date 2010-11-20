import sqlite3
import numpy as np
from timer import Timer
from biology.loaddatatable import fcsextract
from odict import OrderedDict
import sys
import logging
import os.path

def cytof54_values_from_filename(filename):
  filename = os.path.split(filename)[-1]
  filename = filename.replace('concatv3_curated', 'curated')
  vals = OrderedDict()
  vals['filename'] = filename
  filename = filename.replace('.', '_')
  tags = filename.split('_')
  assert tags[0] == 'CyTOF54'
  assert tags[1][:4] == 'Tube'
  vals['tube'] = int(tags[1][4])
  assert tags[2][:3] == 'Day'
  vals['day'] = int(tags[2][3])
  vals['stim'] = tags[3]
  assert tags[4] == 'curated'
  assert tags[5] == 'fcs'
  assert tags[6] == 'eventnum'
  assert tags[7] == 'Ungated'
  print tags[8]
  assert tags[8] == vals['  ']
  vals['normalized'] = 1
  return vals
  
def create_table(db_filename, col_names):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  col_names = ['\'%s\'' % n for n in col_names]
  with Timer('Create Table'):
    sql = 'create table data(%s)' % ', '.join(col_names)
    c.execute(sql)
    logging.info(sql)
    conn.commit()
  conn.close()

def create_indexes(db_filename, col_names):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  with Timer('Create Indexes'):
    for i,v in enumerate(col_names):
      sql = 'CREATE INDEX index%d ON data(%s);' % (i, v)
      c.execute(sql)
      logging.info(sql)
    conn.commit()
  conn.close()

CACHE = {}  
def fcsextrat_cache(fcs_filename):
  global CACHE
  if not fcs_filename in CACHE:
    CACHE[fcs_filename] = fcsextract(fcs_filename)
  return CACHE[fcs_filename]
  
def get_cols(fcs_filename):
  vals_from_filename = cytof54_values_from_filename(fcs_filename)
  fcs_vars, fcs_events = fcsextrat_cache(fcs_filename)
  num_dims = len(fcs_events[0])
  dim_names = [fcs_vars["$P%dS"%(i+1)] for i in xrange(num_dims)]
  cols = vals_from_filename.keys() + dim_names
  return cols, vals_from_filename.keys()
    
def cytof54_create(db_filename, fcs_filename):
  create_table(cols)
  create_indexes(vals_from_filename.keys())
  
def insert_values(db_filename, fcs_filename, filename_values):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  fcs_vars, fcs_events = fcsextrat_cache(fcs_filename)
  with Timer('Insert Values'):
    for i, event in enumerate(fcs_events):
      vals = filename_values + list(event)
      vals = [repr(v) for v in vals]
      c.execute('insert into data values (%s)' % ', '.join(vals))
      if i % 10000 == 0:
        print 'insert into data values (%s)' % ', '.join(vals)
        print i
        conn.commit()
    conn.commit()      
  c.close()

  
if __name__ == '__main__':
  logging.getLogger('').setLevel(logging.DEBUG)
  stream_handler = logging.StreamHandler()
  formatter = logging.Formatter(
      "%(asctime)s - %(levelname)s - %(message)s")
  stream_handler.setFormatter(formatter)
  logging.getLogger('').addHandler(stream_handler)
  if len(sys.argv) < 3:
    print 'Usage: db_converted fcs_dir db_filename'
    exit()
  fcs_dir = sys.argv[1]
  db_filename = sys.argv[2]
  fcs_files = [f for f in os.listdir(fcs_dir) if f.endswith('.fcs')]
  logging.info('Fcs files found:\n%s' % '\n'.join(fcs_files))
  if not fcs_files:    
    raise Exception('No FCS files in the given dir')
  cols_prototype, indexes_prototype = get_cols(os.path.join(fcs_dir, fcs_files[0]))
  if not os.path.exists(db_filename):
    logging.info('Creating table columns and indexes')
    logging.info('Columns for the new table are: %s', ', '.join(cols_prototype))
    create_table(db_filename, cols_prototype)
    logging.info('Table Created')
    create_indexes(db_filename, indexes_prototype)
    logging.info('Indexes Created')
  else:
    logging.info('database exists, no need to create a new one')

  if not os.path.exists('FCS_DONE'):
    fcs_done = ''
  else:
    with open('FCS_DONE', 'r') as fcs_done_file:
      fcs_done = [line.strip() for line in fcs_done_file.readlines()]
  for f in fcs_files:
    if f in fcs_done:
      logging.info('skipping %s because it is in the FCS_DONE list' % f)
      continue
    fcs_path = os.path.join(fcs_dir, f)
    cols, indexes = get_cols(fcs_path)
    assert cols == cols_prototype
    assert indexes == indexes_prototype
    logging.info('Inserting values')
    insert_values(db_filename, fcs_path, cytof54_values_from_filename(fcs_path).values())
    del CACHE[fcs_path]
    with open('FCS_DONE', 'a') as fcs_done_file:
      fcs_done_file.write('\n')
      fcs_done_file.write(f)
  
  
  
  