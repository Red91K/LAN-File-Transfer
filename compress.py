import shutil
import os

ZIPFILEDIRPATH = os.path.abspath("ZipFiles")
FILECACHEDIRPATH = os.path.abspath("FileCache")
RECIEVEDDIRPATH = os.path.abspath("Received")


# input: path of file or directory
# output: "File" or "Dir"
def return_file_or_dir(fullpath) -> str:
    if os.path.isdir(fullpath):
        return "Dir"
    elif os.path.isfile(fullpath):
        return "File"
    else:
        raise Exception("Path does not exist")


# !TODO - return path of compressd
# compresses a directory into the zipfile folder
# /fullpath/filename.extension -> /ZipFiles/filename.zip
def compress_dir(fullpath):
    global ZIPFILEDIRPATH
    fullpath = os.path.abspath(fullpath)

    # name & path of the zipfile to be created
    zipfile_name = os.path.join(ZIPFILEDIRPATH, os.path.basename(fullpath))

    # https://docs.python.org/3/library/shutil.html#archiving-example-with-base-dir
    # base_name = name & path of the zipfile to be created
    # root_dir = the parent directory of the directory to be archived
    # base_dir = the actual directory to be archived
    shutil.make_archive(base_name=zipfile_name,
                        format='zip',
                        root_dir=os.path.dirname(fullpath),
                        base_dir=os.path.basename(fullpath))


# !TODO - return path of uncompressed
# uncompresses a directory into extractDir
def uncompress_dir(fullpath, unpack_dir=RECIEVEDDIRPATH):
    global RECIEVEDDIRPATH
    # https://docs.python.org/3/library/shutil.html
    # fullpath = name & path of file to unpack
    # extract_dir = location of dir to unpack file in
    shutil.unpack_archive(filename=fullpath,
                          format="zip",
                          extract_dir=unpack_dir)


# returns the size (in bytes) of a directory or file
def return_file_or_dir_size(fullpath) -> int:
    if return_file_or_dir(fullpath) == "File":
        filesize = os.path.getsize(fullpath)

    elif return_file_or_dir(fullpath) == "Dir":
        filesize = 0
        for path, dirs, files in os.walk(fullpath):
            for f in files:
                fp = os.path.join(path, f)
                filesize += os.path.getsize(fp)

    return filesize


def return_formated_file_or_dir_size(fullpath) -> str:
    filesize = return_file_or_dir_size(fullpath)
    unitar = ["BYTES", "KB", "MB", "GB", "TB"]
    cur_unitar_position = 0

    for curunit in range(len(unitar)):
        if filesize >= (1000 ** curunit):
            cur_unitar_position = curunit

    return f'{filesize / (1000 ** cur_unitar_position)} {unitar[cur_unitar_position]}'


def print_compare_zip_unzip(zippath, unzippath):
    zipsize = return_file_or_dir_size(zippath)
    unzipsize = return_file_or_dir_size(unzippath)

    print(f'Zipped File is {round(float(zipsize / unzipsize) * 100, 2)}% of Original ({zipsize}/{unzipsize})')


def print_compare_encrypt_original(encrypted_path, original_path):
    encrypt_size = return_file_or_dir_size(encrypted_path)
    original_size = return_file_or_dir_size(original_path)

    print(
        f'Encrypted File is {round(float(encrypt_size / original_size) * 100, 2)}% of Original ({encrypt_size}/{original_size})')


# compresses file or directory, and puts the zip file in the ZipFiles directory
def master_compress(fullpath) -> str:
    global ZIPFILEDIRPATH
    global FILECACHEDIRPATH

    print()
    print("---------------------------------")
    print("(1/3) STARTING COMPRESSION...")
    basename = os.path.basename(fullpath)
    file_or_dir = return_file_or_dir(fullpath)
    target_size = return_file_or_dir_size(fullpath)

    print()
    print(f"Target: {file_or_dir} @ {fullpath}")
    print(f"{basename} is {target_size} bits in size")
    print()

    if file_or_dir == "File":
        # creates a directory within FileCache, with the directory's name being the filename (w/out extension)
        # !TODO - add try-except to catch if FileCache is missing
        no_extension_filename = os.path.splitext(basename)[0]  #
        new_created_dir_in_filecache = os.path.join(FILECACHEDIRPATH, no_extension_filename)

        try:
            os.mkdir(path=new_created_dir_in_filecache)
            print("(1.3/3) FILECACHE DIRECTORY FOUND")
            print(f"(1.6/3) DIRECTORY [{no_extension_filename}] MADE @ {new_created_dir_in_filecache}")
        except Exception as err:
            print(err)
            raise Exception("!FILECACHE DIRECTORY NOT FOUND")

        new_created_zipfile_path_no_extension = os.path.join(new_created_dir_in_filecache, basename)

        # copy file to directory inside FileCache
        shutil.copyfile(fullpath, new_created_zipfile_path_no_extension)
        print(f"(1.9/3) FILE COPIED TO [{no_extension_filename}]")

        # compress directory
        compress_dir(new_created_dir_in_filecache)
        print(f"(2/3) [{no_extension_filename}] COMPRESSED")

        # remove dir from FileCache
        shutil.rmtree(path=new_created_dir_in_filecache)
        print(f"(2.5/3) [{no_extension_filename}] REMOVED")

    elif file_or_dir == "Dir":
        compress_dir(fullpath)
        print(f"(2/3) [{basename}] COMPRESSED")
        no_extension_filename = basename

    print("(3/3) COMPRESSION COMPLETED!")
    print()
    print_compare_zip_unzip(os.path.join(ZIPFILEDIRPATH, no_extension_filename + ".zip"), fullpath)
    print("---------------------------------")

    # returns full absolute path of zipfile
    return os.path.join(ZIPFILEDIRPATH, no_extension_filename + ".zip")


# decompresses a file
def master_uncompress(fullpath) -> str:
    global ZIPFILEDIRPATH
    global RECIEVEDDIRPATH

    print()
    print("---------------------------------")
    print("(1/3) STARTING DECOMPRESSION...")

    if not os.path.exists(fullpath):
        fullpath = os.path.join(ZIPFILEDIRPATH, fullpath)
        if not os.path.exists(fullpath):
            raise Exception("!File not found")
    print("(2/3) TARGET FILE FOUND...")

    print()
    print(f"Target: {fullpath}")
    print(f"{os.path.basename(fullpath)} is {return_file_or_dir_size(fullpath)} bits in size")
    print()

    uncompress_dir(fullpath)
    print("(3/3) DECOMPRESSION FINISHED")
    print("---------------------------------")
    basename = os.path.basename(fullpath)
    no_extension = os.path.splitext(basename)[0]

    # returns name of uncompressed directory
    return os.path.join(RECIEVEDDIRPATH, no_extension)


# clears all files and directories within the specified dir
def clear_directory(path_of_dir: str):
    for filename in os.listdir(path_of_dir):
        file_path = os.path.join(path_of_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')