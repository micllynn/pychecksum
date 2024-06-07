# Introduction

pychecksum contains a set of efficient tracking and checksum calculation tools to
verify the data integrity of files/folders that are being synchronized from local
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
python -m pip install .
```

# Usage
To track a folder with a local and server copy, we initialize a FolderSyncObj
giving it local and server directories.

This computes and stores a pre-transfer directory tree of the server folder,
which is compared with a post-transfer tree after the copying operation to
determine changed files to track:
```python3
import pychecksum as pycs

syncobj = pycs.FolderSyncObj(
	dir_local='/localdrive/folder_original',
	dir_server='/backupdrive/folder_copy')
```

Next, we perform some synchronization event in the terminal to transfer files:
```
>>> rsync, rclone, robocopy, etc. to synchronize local and server folders
```

We can then verify checksums for all files that are new on the server,
using `syncobj.verify_checksums()`.

Internally, this computes a post-transfer directory tree of the server
folder, and compares this to the pre-transfer directory tree to identify any
server files that are new. A checksum calculation is performed on
local/server copies of these new files to verify they have matching checksums.

This method can also optionally delete files where the checksums don't match
(with the `rm_folders_if_integrity_bad` option), allowing for
efficient re-running of the folder sync after.
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
	file: /1/2024-06-04/image1.tiff...
		verifying checksums...
		checksums match.
	------------
	file: /1/2024-06-04/image2.tiff...
		verifying checksums...
		checksums match.
	------------
	file: /1/2024-06-04/image3.tiff...
		verifying checksums...
		checksums match.
	------------
	file: /1/2024-06-04/image4.tiff...
		verifying checksums...
		!!! checksums do not match !!!
	------------
	**** file integrity compromised during transfer *** 
-----------

**** file integrity compromised during transfer **** 
removing folders on server...
are you sure you want to delete /backupdrive/folder_copy/1/2024-06-04/image4.tiff? (y/n) y
deleted /backupdrive/folder_copy/1/2024-06-04/image4.tiff
```

Internally, this calls `pycs.get_checksums()` and `pycs.compare_file_checksums()`
and stores the checksum outputs for each file in `output`.

## Parameters
- `checksum_type=hashlib.sha256` allows specification of the hash algorithm
(any in `hashlib` can be used).
- `rm_folders_if_integrity_bad=True` will automatically remove the folders that
have failed the checksum calculation, allowing quick resynchronization.
- `ask_before_rm=True` will ask before removing folders that have failed the
checksum calculation.
- `verbose=True` prints simple updates about the checksum calculation (as above).
- `verbose_folder_checksums=True` prints the full checksum info for each file:
```
computing checksum of folder_original/file1.tiff...
	sha256 checksum: 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb

computing checksum of folder_original/file2.tiff...
	sha256 checksum: 4523496bd224607ea9f5283494534bcffaf9270e976936c35ca8e3819f85df1e
```


## Output
The `output` contains more granular details on the checksums:
```
print(output.serverpath_transfer_ok)
>> {'/localdrive/folder_original/file1.tiff': False}  # indicates this file failed the checksum calc.
print(output.transfer_ok)
>> False  # indicates at least one folder failed the checksum calc.
```


# Usage with `FolderSyncObj_LocalServerDiff` framework
In this slightly different framework, local and server folders are compared _before_
the transfer: An intelligent diff of the directory trees is performed to see which
folders are only present on the local drive (ie folders that will be
synchronized to the server).

(This is in contrast to FolderSyncObj, which compares only the server's directory tree
before and after a transfer to establish changed files. The choice between either
is a matter of personal taste.)

After the transfer, the checksum calculation is performed on this pre-transfer diff.
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

We can then use the method `syncobj.verify_checksums`. This method recursively
scans all files/folders in each new directory in the diff,
verifies the local and server copies of these new files/folders
have matching checksums, and stores the checksum data for each file/folder in a
dictionary, as well as storing a simple boolean output indicating whether the file
integrity is OK or not.

It can optionally delete server folders where the checksum of any contents
don't match (with the `rm_folders_if_integrity_bad` option), allowing for
efficient re-running of the folder sync after.
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
        /1/2024-06-04/image1.tiff...
			checksum matches.
        /1/2024-06-04/image2.tiff......
			---- checksum does not match ---
-----------

**** file integrity compromised during transfer **** 
removing folders on server...
are you sure you want to delete /backupdrive/folder_copy? (y/n) y
deleted /backupdrive/folder_copy
```

Internally, this calls `pycs.get_folder_checksum()` and `pycs.get_checksum()`
and stores the checksum outputs for each file in `output`.

## Parameters
- `checksum_type=hashlib.sha256` allows specification of the hash algorithm
(any in `hashlib` can be used).
- `rm_folders_if_integrity_bad=True` will automatically remove the folders that
have failed the checksum calculation, allowing quick resynchronization.
- `ask_before_rm=True` will ask before removing folders that have failed the
checksum calculation.
- `verbose=True` prints simple updates about the checksum calculation (as above).
- `verbose_folder_checksums=True` prints the full checksum info for each file:
```
computing checksum of folder_original/file1.tiff...
	sha256 checksum: 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb

computing checksum of folder_original/file2.tiff...
	sha256 checksum: 4523496bd224607ea9f5283494534bcffaf9270e976936c35ca8e3819f85df1e
```


## Output
The `output` contains more granular details on the checksums:
```
print(output.paths)
>> {'/localdrive/folder_original': False}  # indicates this folder failed the checksum calc.
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

