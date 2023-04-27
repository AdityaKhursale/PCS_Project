import utils.constants as constants
import utils.file

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def create_rsa_key_pair(bits=1024):
    # Generates a RSA key pair.
    key = RSA.generate(bits)

    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return private_key, public_key


def encrypt_data(public_key, data):
    public_key_obj = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key_obj)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data


def encrypt_key(public_key, key_to_encrypt):
    public_key_obj = RSA.import_key(public_key)
    key_to_encrypt_obj = RSA.import_key(key_to_encrypt)
    cipher = PKCS1_OAEP.new(public_key_obj)
    encrypted_data = cipher.encrypt(key_to_encrypt_obj.export_key())
    return encrypted_data


def decrypt_data_binary(private_key, encrypted_data):
    public_key_obj = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(public_key_obj)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data


def decrypt_data(private_key, encrypted_data):
    return decrypt_data_binary(private_key, encrypted_data).decode("utf-8")


def create_node_rsa_key_pair():
    private_key_path = constants.private_key_path
    public_key_path = constants.public_key_path

    private_key, public_key = create_rsa_key_pair(8192)

    utils.file.store_file_to_fs(private_key_path, private_key)
    utils.file.store_file_to_fs(public_key_path, public_key)

    return private_key, public_key


def get_node_private_key():
    return utils.file.read_file(constants.private_key_path)
