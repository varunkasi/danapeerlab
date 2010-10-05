import sqlite3
import numpy as np
from timer import Timer
import sys


if len(sys.argv) > 2 and sys.argv[1] == 'create':
  conn = sqlite3.connect(sys.argv[2])
  c = conn.cursor()
  rows = ['r%d' % i for i in xrange(31)]
  with Timer('Create Table'):
    c.execute('create table test(%s)' % ', '.join(rows))
    conn.commit()

  with Timer('Insert Values'):
    for i in xrange(30e6):
      vals = np.random.random(30)
      #print vals
      vals = [v for v in vals]
      if vals[0] < 0.3: vals.append("'A'")
      elif vals[0]<0.6: vals.append("'B'")
      else: vals.append("'C'")
      vals = [str(v) for v in vals]
      c.execute('insert into test values (%s)' % ', '.join(vals))
      if i % 10000 == 0:
        print i
        conn.commit()
        print i
    conn.commit()      
  c.close()
  
elif len(sys.argv) > 2 and sys.argv[1] == 'np_create':
  with Timer('Numpy Create'):
    vals = np.random.random((1e6, 30))
    np.save(sys.argv[2], vals)

elif len(sys.argv) > 2 and sys.argv[1] == 'np_read':  
  vals = []
  with Timer('Numpy read'):  
    for i in xrange(2):
      vals.append(np.load(sys.argv[2]))
    
  
elif len(sys.argv) > 2 and sys.argv[1] == 'read':
  conn = sqlite3.connect(sys.argv[2])
  c = conn.cursor()
  with Timer('Find Values'):   
    c.execute('select * from test where r30="A" limit 300000')   
    rows = c.fetchall()
    print rows[0]
    print len(rows)
  c.close()

elif len(sys.argv) > 2 and sys.argv[1] == 'cytof54_read':
  conn = sqlite3.connect(sys.argv[2])
  c = conn.cursor()
  with Timer('Find Values'):   
    #c.execute('select * from data where day=3')   
    c.execute('select * from data where stim="Dasatinib+Unstim"')
    #c.execute('select * from data where filename=\'CyTOF54_Tube00_Day1_PhosSurfOnly_curated.fcs_eventnum_Ungated_PhosSurfOnly_Day1_normalized_0_Day1_PhosSurfOnly_Singlets.fcs\'')
    rows = c.fetchall()
    print rows[0]
    print len(rows)
  c.close()
  
  
elif len(sys.argv) > 2 and sys.argv[1] == 'index':
  conn = sqlite3.connect(sys.argv[2])
  c = conn.cursor()
  with Timer('Create index'):   
    c.execute('CREATE INDEX index1 ON test(r30);')   
    conn.commit()
    c.close()
   
else:
  print 'usage: read/create filename'