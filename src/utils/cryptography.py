import os

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from utils import file_io as fileIO


def createRsaKeyPair(bits=1024):
    key = RSA.generate(bits)
    privateKey = key.export_key()
    publicKey = key.publickey().export_key()
    return privateKey, publicKey


def encryptData(publicKey, data):
    publicKeyObj = RSA.import_key(publicKey)
    cipher = PKCS1_OAEP.new(publicKeyObj)
    encryptedData = cipher.encrypt(data.encode())
    return encryptedData


def encryptKey(publicKey, keyToEncrypt):
    publicKeyObj = RSA.import_key(publicKey)
    keyToEncryptObj = RSA.import_key(keyToEncrypt)
    cipher = PKCS1_OAEP.new(publicKeyObj)
    encryptedKey = cipher.encrypt(keyToEncryptObj.export_key())
    return encryptedKey


def decryptBinaryData(privateKey, encryptedData):
    publicKeyObj = RSA.import_key(privateKey)
    cipher = PKCS1_OAEP.new(publicKeyObj)
    decryptedData = cipher.decrypt(encryptedData)
    return decryptedData


def decryptData(privateKey, encryptedData):
    return decryptBinaryData(privateKey, encryptedData).decode("utf-8")


def dumpRsaKeyPair(dumpLocation, bits=8192):
    privateKey, publicKey = createRsaKeyPair(bits)
    fileIO.writeBinaryFile(os.path.join(
        dumpLocation, "private_key"), privateKey)
    fileIO.writeBinaryFile(os.path.join(
        dumpLocation, "public_key"), publicKey)
    return privateKey, publicKey
