import os
import re
from utils import constants
import uuid


def generate_file_id(file_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, file_name))


def form_file_path(file_id):
    return constants.dir_path + file_id


def store_file_to_fs(file_path, file_content):
    # Stores to file in binary format.
    create_file_path(file_path)
    fd = open(file_path, "wb")
    fd.write(file_content)
    fd.close()


def read_file(file_path):
    fd = open(file_path, "rb")
    return fd.read()


def create_file_path(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def delete_file(file_path):
    os.remove(file_path)


def is_file_exist(file_path):
    return os.path.isfile(file_path)


def createDir(dirname):
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    except IOError:
        pass
    return os.path.exists(dirname)


def removeFiles(dirname, pattern, raiseException=False):
    try:
        for f in os.listdir(dirname):
            if re.search(pattern, f):
                os.remove(os.path.join(dirname, f))
    except FileNotFoundError as e:
        if raiseException:
            raise (e)
