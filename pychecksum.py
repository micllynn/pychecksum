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

def get_checksum(fname, checksum_type=hashlib.md5(),
                 verbose=False):
    """
    computes checksum of a given file.

    Parameters
    ------------
    checksum_type : str
        Can either be hashlib.md5(),
        hashlib.sha1() or hashlib.sha256()
    verbse : bool
        Whether to print updates or not
    """
    if verbose is True:
        print(f'computing checksum of {fname}... ')
    with open(fname, 'rb') as f:
        while True:
            chunk = f.read(16 * 1024)
            if not chunk:
                break
            checksum_type.update(chunk)
        if verbose is True:
            print(f'\t{checksum_type.name} checksum: {checksum_type.hexdigest()}')

    return checksum_type.hexdigest()


def get_folder_checksum(folder, checksum_type=hashlib.md5(),
                        verbose=False):
    """
    calls get_checksum on all elements of a folder, and stores the outputs
    in a dict.

    Parameters
    -----------
    checksum_type : str
        Can either be hashlib.md5(),
        hashlib.sha1() or hashlib.sha256()
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
                             checksum_type=hashlib.sha256(),
                             verbose=True):
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
        Can either be hashlib.md5(),
        hashlib.sha1() or hashlib.sha256()
    verbose : bool
        Whether to print updates or not (eg files where checksum doesn't match)
    

    Returns True if the checksums match, and False otherwise.
    """
    checksums_pre = get_folder_checksum(folder_pre,
                                        checksum_type=checksum_type,
                                        verbose=verbose)
    checksums_post = get_folder_checksum(folder_post,
                                         checksum_type=checksum_type,
                                         verbose=verbose)

    assert checksums_pre.keys() == checksums_post.keys(), "files don't match"

    if verbose is True:
        print('comparing checksums...')

    matching_checksums = True
    for fname in checksums_pre.keys():
        if verbose is True:
            print(f'\t{fname}...')

        if checksums_pre[fname] != checksums_post[fname]:
            matching_checksums = False
            if verbose is True:
                print(f'\t\t ** checksum for {fname} does not match ** ')

    return matching_checksums
