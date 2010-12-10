#!/usr/bin/env python
import logging
from odict import OrderedDict

_name_to_marker = OrderedDict()

def get_marker_names():
  global _name_to_marker
  return _name_to_marker.keys()
  
def register_marker(name, group='signal', needs_transform=True):
  global _name_to_marker
  _name_to_marker[name] = Marker(name, group, needs_transform)
  return _name_to_marker[name]

def marker_from_name(name):
  return _name_to_marker.get(name, None)

def is_marker_registered(name):
  return name in _name_to_marker
  
class Marker(object):
  def __init__(self, name, group, needs_transform):
    self.name = name
    self.needs_transform = needs_transform
    self.group = group
    
  def __str__(self):
    return self.name

  def __repr__(self):
    arr = [n for n in dir(Markers) if getattr(Markers, n) == self]
    if not arr:
      return "'%s'" % self.name
    else:
      return 'Markers.%s' % arr[0]

def normalize_markers(markers):
  res = []
  for m in markers:
    if isinstance(m, (str, unicode)):
      res.append(marker_from_name(m))
    else:
      res.append(m)
  return res

def get_markers(*groups):
  global _name_to_marker
  return [m.name for m in _name_to_marker.values() if m.group in groups]
  
class Markers:  
  #FSC_A = register_marker('FSC-A')
  #FSC_W	= register_marker('FSC-W')
  #SSC_A	= register_marker('SSC-A')
  #Ax488_A	= register_marker('Ax488-A')
  #PE_A	= register_marker('PE-A')
  #PE_TR_A	= register_marker('PE-TR-A')
  #PerCP_Cy55_A	= register_marker('PerCP-Cy55-A')
  #PE_Cy7_A	= register_marker('PE-Cy7-A')
  #Ax647_A	= register_marker('Ax647-A')
  #Ax700_A	= register_marker('Ax700-A')
  #Ax750_A	= register_marker('Ax750-A')
  #PacBlu_A	= register_marker('PacBlu-A')
  #Qdot525_A	= register_marker('Qdot525-A')
  #PacOrange_A	= register_marker('PacOrange-A')
  #Qdot605_A	= register_marker('Qdot605-A')
  #Qdot655_A	= register_marker('Qdot655-A')
  #Qdot705_A	= register_marker('Qdot705-A')
  Time	= register_marker('Time', 'technical', False)
  Cell_length = register_marker('Cell Length', 'technical', False)
  DNA_191 = register_marker('191-DNA', 'signal')
  DNA_193 = register_marker('193-DNA', 'signal')
  Viability_103 = register_marker('103-Viability', 'signal')
  CD45_115 = register_marker('115-CD45', 'surface')
  CD3_110 = register_marker('110-CD3', 'surface_ignore')
  CD3_111 = register_marker('111-CD3', 'surface_ignore')
  CD3_112 = register_marker('112-CD3', 'surface_ignore')
  CD3_114 = register_marker('114-CD3', 'surface_ignore')
  CD45RA_139 = register_marker('139-CD45RA', 'surface')
  pPLCgamma2_141 = register_marker('141-pPLCgamma2', 'signal')
  CD19_142 = register_marker('142-CD19', 'surface')
  CD11b_144 = register_marker('144-CD11b', 'surface')
  CD4_145 = register_marker('145-CD4', 'surface')
  CD8_146 = register_marker('146-CD8', 'surface')
  CD34_148 = register_marker('148-CD34', 'surface')
  pSTAT5_150 = register_marker('150-pSTAT5', 'signal')
  CD20_147 = register_marker('147-CD20', 'surface')
  Ki67_152 = register_marker('152-Ki67', 'signal')
  pSHP2_154 = register_marker('154-pSHP2', 'signal')
  pERK1_2_151 = register_marker('151-pERK1/2', 'signal')
  pMAPKAPK2_153 = register_marker('153-pMAPKAPK2', 'signal')
  pZAP70_Syk_156 = register_marker('156-pZAP70/Syk', 'signal')
  CD33_158 = register_marker('158-CD33', 'surface')
  CD123_160 = register_marker('160-CD123', 'surface')
  pSTAT3_159 = register_marker('159-pSTAT3', 'signal')
  pSLP_76_164 = register_marker('164-pSLP-76', 'signal')
  pNFkB_165 = register_marker('165-pNFkB', 'signal')
  IkBalpha_166 = register_marker('166-IkBalpha', 'signal')
  CD38_167 = register_marker('167-CD38', 'surface')
  pH3_168 = register_marker('168-pH3', 'signal')
  CD90_170 = register_marker('170-CD90', 'surface')
  pP38_169 = register_marker('169-pP38', 'signal')
  pBtk_Itk_171 = register_marker('171-pBtk/Itk', 'signal')
  pS6_172 = register_marker('172-pS6', 'signal')
  pSrcFK_174 = register_marker('174-pSrcFK', 'signal')
  pCREB_176 = register_marker('176-pCREB', 'signal')
  pCrkL_175 = register_marker('175-pCrkL', 'signal')
  CD3_110_114 = register_marker('110_114-CD3', 'surface')
  EVENT_NUM = register_marker('EventNum', 'technical', False)