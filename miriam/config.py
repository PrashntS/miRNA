import os

static_root = '/repository/project/mir-to-gene/public'
support_dir = os.path.expanduser('~/.miriam')
pickle_dir = os.path.join(support_dir, 'pickles')

os.makedirs(support_dir, exist_ok=True)
os.makedirs(pickle_dir, exist_ok=True)
