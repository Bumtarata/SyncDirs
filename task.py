import shutil, sys, os
from pathlib import Path

class SynchDirs():
    """Class used for synchronizing content of destination directory according
    to source directory"""
    def __init__(self, source_path, destination_path):
        """Initialize all necessary data."""
        # get the paths of source and destination
        self.source_path = source_path
        self.dest_path = destination_path
    
    def _check_contents(self, directory=None):
        """Check contents of directory (self.source_path or self.dest_path).
        If checking source dir, it copies every file of dir to destination dir
        if it isn't already there. If checking destination dir, it removes 
        every file or dir which isn't in source dir."""
        tree = self._get_dir_tree(directory)
        for element in tree:
            if directory == self.source_path:
                element_path_to_check = Path(self.dest_path / element.relative_to(self.source_path))
                if element_path_to_check.exists():
                    if not element.is_dir():
                        src_mtime = element.stat().st_mtime
                        dest_mtime = element_path_to_check.stat().st_mtime
                        if src_mtime != dest_mtime:
                            shutil.copy2(element, element_path_to_check)
                else:
                    if element.is_dir():
                        shutil.copytree(element, element_path_to_check)
                    else:
                        shutil.copy2(element, element_path_to_check)
            
            elif directory == self.dest_path:
                element_path_to_check = Path(self.source_path / element.relative_to(self.dest_path))
                if not element_path_to_check.exists():
                    if element.is_dir():
                        shutil.rmtree(element, ignore_errors=True)
                    else:
                        if element.is_file():
                            element.unlink()
    
    def _get_dir_tree(self, path):
        """Returns list of all files and subdirectories in given direcotry (even
        all files and subfolders in subfolders etc.)"""
        tree = [path]
        for element in tree:
            if element.is_dir():
                for child in element.iterdir():
                    tree.append(child)
        return tree
    
    def synchronize(self):
        """Synchronizes content of self.dest_path according to self.source_path."""
        # Check if destination directory already exists (if this script already
        # run so part of the source directory is copied.
        if not self.dest_path.is_dir():
            # Destination directory doesn't exist so copy the whole source directory
            # tree
            shutil.copytree(self.source_path, self.dest_path)
            
        else:
            # Destination dir exists so call _check_contents for self.dest_path
            # and after that for self.source_path.
            self._check_contents(directory=self.dest_path)
            self._check_contents(directory=self.source_path)
                    
if __name__ == '__main__':
    synch = SynchDirs(Path(sys.argv[1]), Path(sys.argv[2]))
    synch.synchronize()