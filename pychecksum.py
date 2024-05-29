"""
mbfl 24.5.29

This package contains tools to efficiently compute and compare checksums
between files/folders.

It is designed to be used if original, large data files are being backed
up to a server, but there is some possibility of data corruption or loss
during the transfer (ie a simple checksum calculation can be used to
decide whether to re-run the backup or not).

(Written for Lak Lab)
"""
import hashlib
import os
import sys

def get_checksum(fname, checksum_type=hashlib.md5,
                 verbose=False):
    """
    computes checksum of a given file.

    Parameters
    ------------
    checksum_type : str
        Can be hashlib.md5,
        hashlib.sha1, hashlib.sha256, etc.
        (Note that you merely need to provide a class, no need to initialize
        with brackets)
    verbse : bool
        Whether to print updates or not
    """
    checksum = checksum_type()

    if verbose is True:
        print(f'computing checksum of {fname}... ')
    with open(fname, 'rb') as f:
        while True:
            chunk = f.read(16 * 1024)
            if not chunk:
                break
            checksum.update(chunk)
        if verbose is True:
            print(f'\t{checksum.name} checksum: {checksum.hexdigest()}')

    return checksum.hexdigest()


def get_folder_checksum(folder, checksum_type=hashlib.md5,
                        verbose=False):
    """
    calls get_checksum on all elements of a folder, and stores the outputs
    in a dict.

    Parameters
    -----------
    checksum_type : str
        Can be hashlib.md5,
        hashlib.sha1, hashlib.sha256, etc.
        (Note that you merely need to provide a class, no need to initialize
        with brackets)
    verbose : bool
        Whether to print updates or not
    """
    fnames = os.listdir(folder)
    checksums = {}

    for fname in fnames:
        try:
            checksums[fname] = get_checksum(os.path.join(folder, fname),
                                            checksum_type=checksum_type,
                                            verbose=verbose)
            if verbose is True:
                print('')  # necessary to skip a line
        except IsADirectoryError:
            if verbose is True:
                print(f'{fname} is a directory, passing...\n')

    return checksums


def compare_folder_checksums(folder_pre, folder_post,
                             checksum_type=hashlib.sha256,
                             verbose=True,
                             verbose_folder_checksums=False):
    """
    Compares checksums from two folders that should be identical
    (for example, an original data folder and its copy on the server).

    Returns True if checksums match, False otherwise.

    Parameters
    --------------
    folder_pre : str
        Name of the first folder to compare
    folder_post : str
        Name of the second folder to compare
    checksum_type : str
        Can be hashlib.md5,
        hashlib.sha1, hashlib.sha256, etc.
        (Note that you merely need to provide a class, no need to initialize
        with brackets)
    verbose : bool
        Whether to print high-level updates about checksums
        (eg files where checksum doesn't match)
    verbose_folder_checksums : bool
        Whether to print more granular checksum updates
        (precise checksums for each file in the folders)

    Returns True if the checksums match, and False otherwise.
    """
    checksums_pre = get_folder_checksum(folder_pre,
                                        checksum_type=checksum_type,
                                        verbose=verbose_folder_checksums)
    checksums_post = get_folder_checksum(folder_post,
                                         checksum_type=checksum_type,
                                         verbose=verbose_folder_checksums)

    assert checksums_pre.keys() == checksums_post.keys(), "files don't match"

    if verbose is True:
        print('comparing checksums...')

    matching_checksums = True
    for fname in checksums_pre.keys():
        if verbose is True:
            print(f'\t{fname}...', end='\t')

        if checksums_pre[fname] != checksums_post[fname]:
            matching_checksums = False
            if verbose is True:
                print(f' ***** checksum does not match *****  ')
        elif checksums_pre[fname] == checksums_post[fname]:
            if verbose is True:
                print(f'checksum matches.')

    return matching_checksums
