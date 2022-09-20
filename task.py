import shutil, sys, os
from datetime import datetime
from pathlib import Path

import pytz

class SynchDirs():
    """Class used for synchronizing content of destination directory according
    to source directory"""
    def __init__(self, source_path, destination_path, log_file):
        """Initialize all necessary data."""
        # get the paths of source and destination
        self.source_path = source_path
        self.dest_path = destination_path
        self.log_file = log_file
    
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
                            self._log_changes(element, operation='copied')
                else:
                    if element.is_dir():
                        shutil.copytree(element, element_path_to_check)
                    elif element.is_file():
                        shutil.copy2(element, element_path_to_check)
                    
                    self._log_changes(element_path_to_check, operation='copied')
            
            elif directory == self.dest_path:
                element_path_to_check = Path(self.source_path / element.relative_to(self.dest_path))
                if not element_path_to_check.exists() and element.exists():
                    if element.is_dir():
                        shutil.rmtree(element, ignore_errors=True)
                    elif element.is_file():
                        if element.is_file():
                            element.unlink()
                            
                    self._log_changes(element, operation='removed')
    
    def _get_dir_tree(self, path):
        """Returns list of all files and subdirectories in given direcotry (even
        all files and subfolders in subfolders etc.)"""
        tree = [path]
        for element in tree:
            if element.is_dir():
                for child in element.iterdir():
                    tree.append(child)
        return tree
    
    def _log_changes(self, path, operation=None):
        """Method for logging changes made in self.dest_path. Path attribute
        is file or directory which was changed. Operation could be either
        'copied' or 'removed'."""
        if path.is_dir():
            obj = 'Directory'
        else:
            obj = 'File'
        if operation == 'copied':    
            text = f'{obj} {path} was {operation} from {self.source_path / path.relative_to(self.dest_path)}.'
        else:
            text = f'{obj} {path} was {operation}.'
        
        utc = pytz.utc
        cet = pytz.timezone('Europe/Prague')
        time = datetime.now(cet)
        with open(self.log_file, 'a') as file_obj:
            file_obj.write(f'{time}: {text}\n')
        print(f'{time}: {text}')
            
        
        
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
    synch = SynchDirs(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    synch.synchronize()