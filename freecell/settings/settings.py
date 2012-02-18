import os
FREECELL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATLAB_PATH = r'guess'
EXPERIMENTS = {
    'AML with T-Sne data' : (
        os.path.join(os.path.join(FREECELL_DIR), 'aml_tsne', 'aml_tsne.index'),
        ['patient']),
    'Cytof54 erin clustering' : (
        os.path.join(os.path.join(FREECELL_DIR), 'cytof54_clustered_erin', 'cytof54_clustered_erins.index'),
        ['marrow', 'cell_type', 'stim'])}
