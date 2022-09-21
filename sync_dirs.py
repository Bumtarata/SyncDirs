import shutil, sys, time, argparse
from datetime import datetime
from pathlib import Path

import pytz, schedule

class SyncDirs():
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
                # Checking source_path --> something may need to be copied
                element_path_to_check = Path(self.dest_path / element.relative_to(self.source_path))
                if element_path_to_check.exists() and not element.is_dir():
                    src_mtime = element.stat().st_mtime
                    dest_mtime = element_path_to_check.stat().st_mtime
                    if src_mtime != dest_mtime:
                        # Source file and destination file were modified at 
                        # different times, probably they are not the same --> copy
                        self._log_changes(element, operation='copying')
                        shutil.copy2(element, element_path_to_check)
                
                elif element_path_to_check.exists() and element.is_dir():
                    # Currently iterated element exists at destination dir.
                    # Currently iterated element is dir, so just skip this.
                    continue
                
                else:
                    # Currently iterated element doesn't exists at destination dir
                    # so either copy file or copy dir tree.
                    self._log_changes(element, operation='copying')
                    if element.is_dir():
                        shutil.copytree(element, element_path_to_check)
                    elif element.is_file():
                        shutil.copy2(element, element_path_to_check)
            
            elif directory == self.dest_path:
                # Checking dest path --> something may need to be removed
                element_path_to_check = Path(self.source_path / element.relative_to(self.dest_path))
                if not element_path_to_check.exists() and element.exists():
                    # Currently iterated element exists only in dest path, so it
                    # needs to be removed (either just file or whole dir tree)
                    self._log_changes(element, operation='removing')
                    if element.is_dir():
                        shutil.rmtree(element, ignore_errors=True)
                    elif element.is_file():
                        if element.is_file():
                            element.unlink()
    
    def _get_dir_tree(self, path):
        """Returns list of all files and subdirectories in given directory (even
        all files and subfolders in subfolders etc.)"""
        tree = [path]
        # I iterate over a tree list and append to it every file and directory.
        # Every dir appended will get to be iterated, so even deeply nested files
        # will get into the list.
        for element in tree: 
            if element.is_dir():
                for child in element.iterdir():
                    tree.append(child)
        return tree
    
    def _log_changes(self, path, operation=None):
        """Method for logging changes made in self.dest_path. Path attribute
        is file or directory which was changed. Operation could be either
        'copying' or 'removing'."""
        if path.is_dir():
            obj = 'directory'
        else:
            obj = 'file'
        
        if operation == 'copying':    
            try:
                text = f'{operation.capitalize()} {path} {obj} to {self.dest_path / path.relative_to(self.source_path)}.'
            except ValueError:
                # Copying source directory to destination path.
                text = f'{operation.capitalize()} {path} {obj} to {self.dest_path}.'
        elif operation == 'removing':
            text = f'{operation.capitalize()} {path}.'
        
        cet = pytz.timezone('Europe/Prague')
        time = datetime.now(cet)
        with open(self.log_file, 'a') as file_obj:
            file_obj.write(f'{time}: {text}\n')
        print(f'{time}: {text}')
        
    def synchronize(self):
        """Synchronizes content of self.dest_path according to self.source_path."""
        # Check if destination directory already exists (if this script already
        # run --> part of the source directory is copied).
        if not self.dest_path.is_dir() and not self.dest_path.is_file():
            # Destination directory doesn't exist so copy the whole source directory
            # tree
            self._log_changes(self.source_path, operation='copying')
            shutil.copytree(self.source_path, self.dest_path)
            
        elif self.dest_path.is_dir():
            # Destination dir exists so call _check_contents for self.dest_path
            # and after that for self.source_path.
            self._check_contents(directory=self.dest_path)
            self._check_contents(directory=self.source_path)
        
        else:
            # self.dest_path leads to file --> can't create files and folders
            # inside a file --> stop script
            print("Exception: Destination path can't lead to a file (it needs to lead to directory).")
            sys.exit()
                    
if __name__ == '__main__':
    desc = 'Synchronize destination dir to exactly match the source dir.'
    usage_text = '%(prog)s: [-h] (-u {seconds, minutes, hours} -n | -o) source destination log_file'
    parser = argparse.ArgumentParser(description=desc, usage=usage_text)
    parser.add_argument('source', help='path to the source directory')
    parser.add_argument('destination',
        help='path to the destination directory (if leads to non_existent dir, it will be created)')
    parser.add_argument('log_file', help='path to a file where script will write logs')
    parser.add_argument('-n', '--number', type=int, help='number; length of interval between each sync repeat')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--unit', choices=['seconds', 'minutes', 'hours'],
        help='choose time unit used to caltulation of sync repeat interval')
    group.add_argument('-o', '--once', action='store_true', help='run synchronization only once')
    args = parser.parse_args()
    
    if args.unit and not args.number:
        print("Exception: With -unit must be also provided -number")
        sys.exit()
    
    sync = SyncDirs(
        Path(args.source).resolve(),
        Path(args.destination).resolve(),
        Path(args.log_file).resolve()
        )
    if not sync.source_path.exists():
        # Check if source path is valid.
        print("Exception: Source path doesn't exists, please try again with existing source path.")
        sys.exit()
        
    sync.synchronize()
    
    if not args.once:
        time_unit = args.unit
        
        if time_unit == 'seconds':
            schedule.every(args.number).seconds.do(sync.synchronize)
        elif time_unit == 'minutes':
            schedule.every(args.number).minutes.do(sync.synchronize)
        elif time_unit == 'hours':
            schedule.every(args.number).hours.do(sync.synchronize)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                schedule.cancel_job(sync.synchronize)
                print('Ending sync_dirs.py')
                break