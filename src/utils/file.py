import os
import utils.constants as constants
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
