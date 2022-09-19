import shutil, sys
from pathlib import Path

# get the paths of source and destination
source_path = Path(sys.argv[1])
dest_path = Path(sys.argv[2])

# Check if destination directory already exists (if this script already
# run so part of the source directory is copied.
if not dest_path.is_dir():
    # Destination directory doesn't exist so copy the whole source directory
    # tree
    shutil.copytree(source_path, dest_path)
    
else:
    # Destination dir exists so for every file or dir in source dir check if
    # it also is in destination dir and if it isn't there, copy it.
    for child in source_path.iterdir():
        dest_path_of_child = dest_path / child.name
        if dest_path_of_child.exists():
            continue
        else:
            if child.is_dir():
                shutil.copytree(child, dest_path_of_child)
            else:
                shutil.copy2(child, dest_path)