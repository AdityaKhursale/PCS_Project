from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes


def create_rsa_key_pair():
    # Generates a RSA key pair.
    key = RSA.generate(2048)

    private_key = key.export_key().decode("utf-8")
    public_key = key.publickey().export_key().decode("utf-8")

    return private_key, public_key


def encrypt_data(public_key, data):
    # @TODO
    return data


def decrypt_data(private_key, encrypted_data):
    # @TODO
    return encrypted_data
