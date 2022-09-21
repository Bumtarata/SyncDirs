# SyncDirs

SyncDirs is a simple script for repeatedly one-way synchronization of two folders.
At start and then after given time interval it looks into destination directory
and compares its content with source directory. If there is anything missing or
absent in destination directory it is copied there or removed from there respectively.
Files are also copied if last modified time of file in source directory is different
than last modified time of corresponding file in destination directory.
Right before any change in destination directory is made, to console and to
given file is written log whether a file or directory is being copied or removed.
You can end the script easily by KeyBoard interrupt (usually ctrl+c).

I made this script as a homework task for my first job interview. Exact wording
of a task can be found in task.docx.

## Installation, dependencies and running script

This script was written in Python 3.10.5. It might run on older versions but
backward compatibility wasn't tested and the script wasn't created with
backward compatibility on mind.

### Dependencies
For running it you need to install pytz and schedule modules.
Just type following command to commandline:

```bash
pip install -r requirements.txt
```

### Running script

Run command:

```bash
python sync_dirs.py [source directory] [destination directory] [log_file] [number] [time unit]
```

Source directory should a path to directory which contents will be checked and
copied into destination directory if needed.

Destination directory should be a path to a directory where exact replica of
contents of a source directory. If path leads to a non-existent directory it will
be created (also with all parent directories if needed).

Log_file should be a path leading to a file where the script will write all changes.

Number is used with time unit to calculate how often should script synchronize
files.

Time unit could be either seconds, minutes or hours.

## License

MIT License

Copyright (c) 2022 Stránský Jakub