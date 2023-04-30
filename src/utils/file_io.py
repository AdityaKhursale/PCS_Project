import os
import re
import shutil
import uuid


def getFileId(fileName):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, fileName))


def writeBinaryFile(filePath, fileContent):
    if createDir(os.path.dirname(filePath)):
        with open(filePath, "wb") as f:
            f.write(fileContent)


def readBinaryFile(filePath):
    fileContent = b""
    if fileExists(filePath):
        with open(filePath, "rb") as f:
            fileContent = f.read()
    return fileContent


def writeFile(filePath, fileContent):
    if createDir(os.path.dirname(filePath)):
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(fileContent)


def readFile(filePath):
    fileContent = ""
    if fileExists(filePath):
        with open(filePath, "r", encoding="utf-8") as f:
            fileContent = f.read()
    return fileContent


def deleteFile(filePath):
    os.remove(filePath)


def fileExists(filePath):
    return os.path.isfile(filePath)


def moveFile(src, dest):
    return shutil.move(src, dest)


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
            raise e
