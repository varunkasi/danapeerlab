#!/usr/bin/env python
import logging
from odict import OrderedDict

_name_to_marker = OrderedDict()

def get_marker_names():
  global _name_to_marker
  return _name_to_marker.keys()
  
def register_marker(names, group='signal', needs_transform=True):
  global _name_to_marker
  marker = Marker(names, group, needs_transform)
  for name in names:
    _name_to_marker[name] = marker
  return marker


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def normalize_marker_name(name):
  if name in ('110-CD3', '(Cd110)Dd'):
    return 'CD3-110'
  if name in ('111-CD3', '(Cd111)Dd'):
    return 'CD3-111'
  if name in ('112-CD3', '(Cd112)Dd'):
    return 'CD3-112'
  if name in ('114-CD3', '(Cd114)Dd'):
    return 'CD3-114'
  if name in ('110_114-CD3',):
    return 'CD3'
  if name in ('191-DNA', ):
    return 'DNA-191'
  if name in ('193-DNA', ):
    return 'DNA-193'

    
  if name.endswith('Dd'):
    name = name[:-2]
  if name.endswith(')'):
    name = name.split('(')[0]
  if name.endswith('-B'):
    name = name[:-2] + 'b' 
  if is_int(name[:3]) and name[3] == '-':
    name = name[4:]
  return name
  
  
def marker_from_name(name):
  norm_name = normalize_marker_name(name)
  if not norm_name in _name_to_marker:
    pass
    #logging.error('Could not find marker name %s (%s)' % (name, norm_name))
  return _name_to_marker.get(norm_name, None)

def is_marker_registered(name):
  return name in _name_to_marker
  
class Marker(object):
  def __init__(self, names, group, needs_transform):
    self.names = names
    self.needs_transform = needs_transform
    self.group = group
    
  def __str__(self):
    return self.names[0]

  def __repr__(self):
    arr = [n for n in dir(Markers) if getattr(Markers, n) == self]
    if not arr:
      return "'%s'" % self.names[0]
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
  return [m.names[0] for m in _name_to_marker.values() if m.group in groups]
  
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
  T_SNE_1	= register_marker(('t-SNE 1',), 'other', False)
  T_SNE_2	= register_marker(('t-SNE 2',), 'other', False)
  sample_source	= register_marker(('sample_source',), 'other', False)
  Time	= register_marker(('Time',), 'technical', False)
  Cell_length = register_marker(('Cell Length', 'Cell_length'), 'technical', False)
  DNA_191 = register_marker(('DNA-191', '191-DNA', 'DNA1'), 'signal_ignore')
  DNA_193 = register_marker(('DNA-193', '193-DNA', 'DNA2'), 'signal_ignore')
  Viability_103 = register_marker(('Viability', '103-Viability'), 'signal_ignore')
  CD45_115 = register_marker(('CD45', '115-CD45'), 'surface')
  CD3_110 = register_marker(('CD3-110', '110-CD3'), 'surface_ignore')
  CD3_111 = register_marker(('CD3-111', '111-CD3'), 'surface_ignore')
  CD3_112 = register_marker(('CD3-112', '112-CD3'), 'surface_ignore')
  CD3_114 = register_marker(('CD3-114', '114-CD3'), 'surface_ignore')
  CD45RA_139 = register_marker(('CD45RAb', 'CD45RA', '139-CD45RA'), 'surface')
  pPLCgamma2_141 = register_marker(('pPLCgamma2', '141-pPLCgamma2'), 'signal')
  CD19_142 = register_marker(('CD19', '142-CD19'), 'surface')
  CD11b_144 = register_marker(('CD11b', '144-CD11b'), 'surface')
  CD4_145 = register_marker(('CD4', '145-CD4'), 'surface')
  CD8_146 = register_marker(('CD8', '146-CD8'), 'surface')
  CD34_148 = register_marker(('CD34', '148-CD34'), 'surface')
  pSTAT5_150 = register_marker(('pSTAT5', '150-pSTAT5'), 'signal')
  CD20_147 = register_marker(('CD20', '147-CD20'), 'surface')
  Ki67_152 = register_marker(('Ki67', '152-Ki67'), 'signal')
  pSHP2_154 = register_marker(('pSHP2','154-pSHP2'), 'signal')
  pERK1_2_151 = register_marker(('pERK1/2', '151-pERK1/2'), 'signal')
  pMAPKAPK2_153 = register_marker(('pMAPKAPK2', '153-pMAPKAPK2'), 'signal')
  pZAP70_Syk_156 = register_marker(('pZAP70/Syk', '156-pZAP70/Syk'), 'signal')
  CD33_158 = register_marker(('CD33', '158-CD33'), 'surface')
  CD123_160 = register_marker(('CD123', '160-CD123'), 'surface')
  pSTAT3_159 = register_marker(('pSTAT3', '159-pSTAT3'), 'signal')
  pSLP_76_164 = register_marker(('pSLP-76', '164-pSLP-76'), 'signal')
  pNFkB_165 = register_marker(('pNFkB', '165-pNFkB'), 'signal')
  IkBalpha_166 = register_marker(('IkBalpha', '166-IkBalpha'), 'signal')
  CD38_167 = register_marker(('CD38', '167-CD38'), 'surface')
  pH3_168 = register_marker(('pH3', '168-pH3'), 'signal')
  CD90_170 = register_marker(('CD90', '170-CD90'), 'surface')
  pP38_169 = register_marker(('pP38', '169-pP38'), 'signal')
  pBtk_Itk_171 = register_marker(('pBtk/Itk', '171-pBtk/Itk'), 'signal')
  pS6_172 = register_marker(('pS6', '172-pS6'), 'signal')
  pSrcFK_174 = register_marker(('pSrcFK', '174-pSrcFK'), 'signal')
  pCREB_176 = register_marker(('pCREB', '176-pCREB'), 'signal')
  pCrkL_175 = register_marker(('pCrkL', '175-pCrkL'), 'signal')
  CD3_110_114 = register_marker(('CD3', '110_114-CD3'), 'surface')
  CD133_141 = register_marker(('CD133',), 'surface')
  CD49d_144 = register_marker(('CD49d',), 'surface')
  IGD = register_marker(('IgD',), 'surface')
  CD79b = register_marker(('CD79b',), 'surface')
  FLT3 = register_marker(('Flt3',), 'surface')
  CD2 = register_marker(('CD2',), 'surface')
  CD5 = register_marker(('CD5',), 'surface')
  CD123b = register_marker(('CD123b',), 'surface')
  CD64 = register_marker(('CD64',), 'surface')
  LA_OX = register_marker(('La-Ox',), 'surface')
  LA_OX = register_marker(('La-Ox',), 'surface')
  CD114 = register_marker(('CD114',), 'surface')
  CD14 = register_marker(('CD14',), 'surface')
  CD38b = register_marker(('CD38b',), 'surface')
  CD15 = register_marker(('CD15',), 'surface')
  CD16b = register_marker(('CD16b',), 'surface')
  CD44 = register_marker(('CD44',), 'surface')
  CD7 = register_marker(('CD7',), 'surface')
  CD22 = register_marker(('CD22',), 'surface')
  CD56 = register_marker(('CD56',), 'surface')
  TIM3b = register_marker(('TIM3b',), 'surface')
  CD117 = register_marker(('CD117',), 'surface')
  CD47 = register_marker(('CD47',), 'surface')
  HLADR = register_marker(('HLADR',), 'surface')
  ERROR = register_marker(('error', 'Cd'), 'surface_ignore')
  EVENT_NUM = register_marker(('EventNum', 'event number'), 'technical', False)