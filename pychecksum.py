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
import pathlib
import filecmp
import shutil
import os
import sys

if sys.version_info.major >= 3 and sys.version_info.minor >=3:
    from types import SimpleNamespace
else:
    class SimpleNamespace:
        pass

def get_rel_path(folder, parent_folder):
    return os.path.normpath(str(folder)).split(
        os.path.normpath(str(parent_folder)))[1]


class TrackDir(object):
    def __init__(self, path):
        """An object for keeping track of directories
        before and after significant changes (eg copy from
        local drive to server).

        - ls_new() returns a set of PathObjects
        in directory that has changed from when the DirCompare
        instance was initialized to the present

        - rm_new() removes all directories that have changed
        from when the DirCompare instance was initialized to
        the present

        Parameters
        ------------
        directory : str
            Path to a directory to monitor
        """
        self.path = path
        self.path_obj = SimpleNamespace()
        self.folders = SimpleNamespace()

        self.path_obj.pre = pathlib.Path(self.path)
        self.folders.pre = [x for x in
                            self.path_obj.pre.rglob('*') if x.is_dir()]

    def _log_state(self):
        """Logs the state of the filetree within self.directory"""
        self.path_obj.post = pathlib.Path(self.path)
        self.folders.post = [x for x in
                             self.path_obj.post.rglob('*') if x.is_dir()]

    def ls_new(self):
        """Returns a list of directories that are new
        in the filetree of self.directory since the object
        was initialized"""
        self._log_state()

        set_pre = set(self.folders.pre)
        set_post = set(self.folders.post)

        folder_diffs = list(set_post - set_pre)

        return folder_diffs

    def rm_new(self):
        """Removes all new directories
        in the filetree of self.directory since the object
        was initialized"""
        folder_diffs = self.ls_new()

        for folder_diff in folder_diffs:
            shutil.rmtree(folder_diff, ignore_errors=True)

        return


class FolderSyncObj(object):
    def __init__(self, dir_local, dir_server,
                 verbose=True,
                 print_level='\t'):
        """
        Object to track a folder which will be synchronized between a
        local drive and the server.

        Two directories should be provided, a local and server path.
        These should be identical except that the local
        copy should have more folders that are not on the server yet
        (but will be during an upcoming transfer operation.)

        Expected usage:
        =============
        syncobj = FolderSyncObj(dir_local='/Users/test/folder_localcopy',
                                dir_local='/Server/folder_servercopy')
        >> # do some sync stuff like rsync, robocopy, etc. between the folders

        output = syncobj.verify_checksums(verbose=True)
        >> comparing checksums...
        >> 	script1.py...	checksum matches.
        >> 	script2.py...	 ***** checksum does not match ***** 

        print(output.transfer_ok)
        >> False

        Parameters
        ----------
        dir_local : str
            String corresponding to local directory
        dir_server : str
            String corresponding to server directory
        """
        if verbose is True:
            print(print_level+
                  'setting up FolderSyncObj...')
            print(print_level+'\t'+
                  'local folder: {}'.format(dir_local))
            print(print_level+'\t'+
                  'server folder: {}'.format(dir_server))

        # setup
        self.path = SimpleNamespace()
        self.path.local = dir_local
        self.path.server = dir_server

        self.path_compare = filecmp.dircmp(self.path.local,
                                      self.path.server)

        self.diff_fullpath = SimpleNamespace()
        
        try:
            self.diff_fullpath.local = self.get_diffs_localpaths()
            self.diff_fullpath.server = self.get_diffs_serverpaths()
        except FileNotFoundError:
            print('one of the inputs is not a directory')

    def list_diffs(self):
        """
        List all folders that are only in local, not in server
        (lists relative paths to dir_local, not complete path)
        """
        return self.path_compare.left_only

    def get_diffs_localpaths(self):
        """
        For all folders that are different (ie only on local),
        get the full local paths for these folders and store in a list
        """
        local_folders = self.list_diffs()
        local_folders_fullpath = []
        for local_folder in local_folders:
            local_folders_fullpath.append(
                os.path.join(self.path.local, local_folder))

        return local_folders_fullpath

    def get_diffs_serverpaths(self):
        """
        For all folders that are different (ie only on local),
        get the full expected server paths for these folders and store in a list.

        (Expected server paths are generated based on the root server path provided.
        """
        local_folders = self.list_diffs()
        server_folders_fullpath = []
        for local_folder in local_folders:
            server_folders_fullpath.append(os.path.join(self.path.server, local_folder))

        return server_folders_fullpath

    def verify_checksums(self, checksum_type=hashlib.sha256,
                         verbose=True, verbose_folder_checksums=False,
                         rm_folders_if_integrity_bad=False,
                         ask_before_rm=True,
                         recursive_comp=True,
                         print_level='\t'):
        """Call this method after the files have been transferred from local
        to server. Performs checksum computation on all files that have been
        newly transferred from local to server, prints updates on whether
        the checksums match, and returns an object that summarizes
        the checksum computation.

        Parameters
        -----------
        checksum_type : str
            Can be hashlib.md5,
            hashlib.sha1, hashlib.sha256, etc.
            (Note that you merely need to provide a class, no need to initialize
            with brackets)
        verbse : bool
            Whether to print updates or not
        verbose_folder_checksums : bool
            Whether to print granular updates about the individual folder checksums

        Returns
        -----------
        checksum_obj : SimpleNamespace
            checksum_obj.paths : dict
                Comprises of a dictionary of named local directories
                and whether they are correctly transferred (True) or not (False)
            checksum_obj.transfer_ok : bool
                Returns True if all folders are transferred correclty,
                False otherwise
        """

        checksum_obj = SimpleNamespace()
        checksum_obj.paths = {}
        checksum_obj.transfer_ok = True

        for ind, local_folder in enumerate(self.diff_fullpath.local):
            if verbose == True:
                print(print_level+'local folder: {}...'.format(self.diff_fullpath.local[ind]))
                print(print_level+'server folder: {}...'.format(self.diff_fullpath.server[ind]))
                print('verifying checksums...\n-------------')
            checksum_obj.paths[local_folder] = compare_folder_checksums(
                self.diff_fullpath.local[ind],
                self.diff_fullpath.server[ind],
                checksum_type=checksum_type,
                verbose=verbose,
                verbose_folder_checksums=verbose_folder_checksums,
                recursive=recursive_comp)

            if checksum_obj.paths[local_folder] == False:
                 checksum_obj.transfer_ok = False
            print(print_level+'------------')

        if checksum_obj.transfer_ok == False:
            if verbose == True:
                print('\n'+print_level+
                      '**** file integrity compromised during transfer **** ')
            if rm_folders_if_integrity_bad == True:
                print(print_level+
                      'removing folders on server...')
                self.rm_new_folders(ask_before_rm=ask_before_rm,
                                    print_level=print_level)
        elif checksum_obj.transfer_ok == True:
            if verbose == True:
                print(print_level+
                      '**** file integrity ok ****')
            
        return checksum_obj

    def rm_new_folders(self, ask_before_rm=True, print_level='\t'):
        """Removes all new folders in Server that were created during the
        transfer process (ie when the folder was started to be tracked)
        """
        diffs_serverpath = self.get_diffs_serverpaths()

        for path in diffs_serverpath:
            if ask_before_rm is True:
                check = input(print_level
                              +'are you sure you want to delete {}? (y/n)'
                              .format(path))
                if check == 'y':
                    shutil.rmtree(path, ignore_errors=True)
                    print(print_level
                          +'deleted {}'.format(path))
                else:
                    pass
            elif ask_before_rm is False:
                shutil.rmtree(path, ignore_errors=True)
                print(print_level
                      +'deleted {}'.format(path))
        return


def get_checksum(fname, checksum_type=hashlib.sha256,
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
        print('computing checksum of {}... '.format(fname))
    with open(fname, 'rb') as f:
        while True:
            chunk = f.read(16 * 1024)
            if not chunk:
                break
            checksum.update(chunk)
        if verbose is True:
            print('\t{} checksum: {}'.format(
                checksum.name, checksum.hexdigest()))

    return checksum.hexdigest()


def get_folder_checksum(folder, checksum_type=hashlib.sha256,
                        recursive=True,
                        include_hidden=False,
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
    if recursive is False:
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
                    print('{} is a directory, passing...\n'.format(fname))

    if recursive is True:
        path_obj = pathlib.Path(folder)

        if include_hidden is False:
            path_files = [x.resolve() for x in path_obj.rglob('*')
                          if x.is_file()
                          and not str(os.path.split(str(x.resolve()))[-1]).startswith('.')]
        elif include_hidden is True:
            path_files = [x.resolve() for x in path_obj.rglob('*')
                          if x.is_file()]
        
        checksums = {}
        checksums_pathobj = []

        for path_file in path_files:
            if verbose is True:
                print('file: {}, folder: {}'.format(path_file, folder))
            _rel_path = get_rel_path(path_file, folder)
            checksums[_rel_path] = get_checksum(
                str(path_file),
                checksum_type=checksum_type,
                verbose=verbose)

    return checksums


def compare_folder_checksums(folder_pre, folder_post,
                             checksum_type=hashlib.sha256,
                             verbose=True,
                             verbose_folder_checksums=False,
                             recursive=True):
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
                                        verbose=verbose_folder_checksums,
                                        recursive=recursive)
    checksums_post = get_folder_checksum(folder_post,
                                         checksum_type=checksum_type,
                                         verbose=verbose_folder_checksums,
                                         recursive=recursive)

    assert checksums_pre.keys() == checksums_post.keys(), "files don't match"

    matching_checksums = True
    for fname in checksums_pre.keys():
        if verbose is True:
            print('{}...'.format(fname))

        if checksums_pre[fname] != checksums_post[fname]:
            matching_checksums = False
            if verbose is True:
                print('\t---- checksum does not match -------')
        elif checksums_pre[fname] == checksums_post[fname]:
            if verbose is True:
                print('\tchecksum matches.')

    # if verbose is True and matching_checksums is True:
    #     print('*** checksums match for all files *** ')
    # if verbose is True and matching_checksums is False:
    #     print('*** checksums DO NOT match for all files *** ')

    return matching_checksums
