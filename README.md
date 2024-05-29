# Introduction

pychecksum contains a set of simple tools to efficiently compute and
compare checksums of files or folders.

It is designed to be used if large folders are being copied to a server,
but there is some possibility of corruption. By comparing checksums
of the original and copied folders, users can decide whether any files
are corrupted and whether the folder copy operation needs to be rerun.

# Installation
```python3
git clone https://github.com/micllynn/pychecksum
cd pychecksum
python3 setup.py install
```

# Usage
```python3
import pychecksum as pycs

result = pycs.compare_folder_checksums(
	'localdrive/folder_original',
	'backupdrive/folder_copy')
```

This will output `result=True` if the checksums for each file in the folder match,
and `result=False ` otherwise.

# More advanced options:

## Change the checksum type
By default, pychecksum uses the sha256 hash type. This can be changed
to any hash type found in hashlib, including md5 (probably quicker):
```python3
result = pycs.compare_folder_checksums(
	'localdrive/folder_original',
	'backupdrive/folder_copy',
	checksum_type=hashlib.md5(),
	verbose=True)
```

`verbose=True` will print an update of which files are currently being
checksum-verified, and which ones the checksum doesn't match for.


## Compare individual files
```python3
result = pycs.get_checksum(
	'localdrive/folder_original/some_file.tiff'
	checksum_type=hashlib.md5(),
	verbose=False)
```
For more granular control, this outputs the actual checksum for a particular
named file.
