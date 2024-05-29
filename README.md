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
to any hash type found in hashlib, including md5:
```python3
result = pycs.compare_folder_checksums(
	'localdrive/folder_original',
	'backupdrive/folder_copy',
	checksum_type=hashlib.md5)
```

## Output more information about checksums that don't match
`verbose=True` will print an update of which files are currently being
checksum-verified, and which ones the checksum doesn't match for.
`verbose_folder_checksums=True` will print a granular update of the checksum
values for each individual file in the folder

```python3
result = pycs.compare_folder_checksums(
	'localdrive/folder_original',
	'backupdrive/folder_copy',
	verbose=True,
	verbose_folder_checksums=False)
```

`verbose` output:
```
comparing checksums...
	file1.tiff...	checksum matches.
	file2.tiff...	checksum matches.
	file3.tiff...	 ***** checksum does not match *****
	file4.tiff...	checksum matches.
	file5.tiff...	checksum matches.
```

`verbose_folder_checksums` output:
```
computing checksum of folder_original/file1.tiff...
	sha256 checksum: 13b7e800bd1530ee31459e0c8f7876fff9cd993f6fce718a5eee622429c222bb

computing checksum of folder_original/file2.tiff...
	sha256 checksum: 4523496bd224607ea9f5283494534bcffaf9270e976936c35ca8e3819f85df1e
```

## Get checksum of individual files or folders
For more granular control, this outputs the actual checksum for a particular
named file:
```python3
result = pycs.get_checksum(
	'localdrive/folder_original/some_file.tiff'
	checksum_type=hashlib.sha256,
	verbose=True)
```

And a dictionary of checksum values for each file in a folder:
```python3
result = pycs.get_folder_checksum(
	'localdrive/folder_original'
	checksum_type=hashlib.sha256,
	verbose=True)
```
