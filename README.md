# Introduction

pychecksum contains a set of efficient tracking and checksum calculation tools to
verify the data integrity of folders that are being synchronized from local
hard drives to a server.

Folders are tracked and verified in an object-oriented framework,
and if checksum calculations don't match, the new subfolders
can be automatically deleted for subsequent resynchronization.

More granular tools are also included for computing checksums on
individual files or folders without direct comparison.

# Installation
```python3
git clone https://github.com/micllynn/pychecksum
cd pychecksum
python3 -m pip install .
```

# Usage
First, we initialize a sync object to track a folder with a local and server copy.
This performs a diff of the directory trees to see which folders are only
present on the local drive (ie will be synchronized to the server).
```python3
import pychecksum as pycs

syncobj = pycs.FolderSyncObj(
	dir_local='/localdrive/folder_original',
	dir_server='/backupdrive/folder_copy')
```

Next, we perform some synchronization event in the terminal:
```
>>> rsync, rclone, robocopy, etc. to synchronize local and server folders
```

We can then use the method `syncobj.verify_checksums` to ensure that
newly copied folders to the server have matching checksums to the originals:
```python3
output = syncobj.verify_checksums(
	checksum_type=hashlib.sha256,
	rm_folders_if_integrity_bad=True,
	ask_before_rm=True)
```

Which prints the following updates:
```
local folder: /localdrive/folder_original...
server folder: /backupdrive/folder_copy...
comparing checksums...
        script1.py...	checksum matches.
        script2.py...	 ***** checksum does not match ***** 
----------

**** file integrity compromised during transfer **** 
removing folders on server...
	are you sure you want to delete /backupdrive/folder_copy? (y/n) y
		deleted /backupdrive/folder_copy

```

Note that `rm_folders_if_integrity_bad` will automatically remove the folders that
have failed the checksum calculation (with a prompt), for ease of resynchronization.
(This can be turned off, as can `ask_before_rm=True`.)

The `output` contains more granular details on the checksums:
```
print(output.paths)
>> {'/localdrive/folder_original': False}  # indicates this fodler failed the checksum calc.
print(output.transfer_ok)
>> False  # indicates at least one folder failed the checksum calc.
```

# More advanced functions:
## `pycs.compare_folder_checksums`
This allows for a manual checksum calculation between folders.

```python3
result = pycs.compare_folder_checksums(
	'folder1',
	'folder2',
	checksum_type=hashlib.md5	
	verbose=True,
	verbose_folder_checksums=False)
```

```
print(result)
>>> True  # Returns true if the folder checksums match
```


The `verbose_folder_checksums` option prints the full checksum for each file:
```
computing checksum of folder_original/file1.tiff...
	sha256 checksum: 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb

computing checksum of folder_original/file2.tiff...
	sha256 checksum: 4523496bd224607ea9f5283494534bcffaf9270e976936c35ca8e3819f85df1e
```

## `pycs.get_checksum`
This computes a checksum for an individual file.

```python3
result = pycs.get_checksum(
	'localdrive/folder_original/some_file.tiff'
	checksum_type=hashlib.sha256,
	verbose=True)
```

```
print(result)
>>> 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb
```

## `pycs.get_folder_checksum`
This returns a dictionary of checksum values for each file in a folder:
```python3
result = pycs.get_folder_checksum(
	'localdrive/folder_original'
	checksum_type=hashlib.sha256,
	verbose=True)
```

```
print(result)
>>> {'file1': 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb,
	 'file2': 4523496bd224607ea9f5283494534bcffaf9270e976936c35ca8e3819f85df1e}
```

