import os
FREECELL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATLAB_PATH = r'guess'
EXPERIMENTS = {
    'AML with T-Sne data' : (
        r'/Users/daniv/projects/data/aml_tsne/aml.index',
        ['patient']),
    'cytof54 erin clustering' : (
        r'/Users/daniv/projects/data/cytof54_clustered_erin/cytof54.index',
        ['marrow', 'cell_type', 'stim'])}
