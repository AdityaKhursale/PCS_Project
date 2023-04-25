import re
import sys

from distributed_fs import distributed_fs_pb2
from utils.decorators import useDistributedFileSystemStub

# TODO: Use better naming


class Action:
    def __init__(self, command, filename=None, options=None):
        self.command = command
        self.filename = filename
        self.options = options


class ActionPerformer:

    serverAddress = ""

    @staticmethod
    def printHelp(**kwargs):
        # pylint: disable=unused-argument
        helpMenu = """
            print help          help
            create file         create <filename>
            read file           read <filename>
            write to file       update <filename> < "text"
            append to file      update <filename> << "text"
            delete file         delete <filename>
            list files          list
            grant permissions   permit <filename> <hostname> <read/write>
            exit client         exit
        """
        print(helpMenu)
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def createFile(**kwargs):
        stub = kwargs["stub"]
        stub.CreateFile(distributed_fs_pb2.CreateRequest(
            filename=kwargs['filename']))
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def readFile(**kwargs):
        stub = kwargs["stub"]
        resp = stub.ReadFile(distributed_fs_pb2.ReadRequest(
            filename=kwargs['filename']))
        print(f"\n\n{resp.filecontent}\n\n")
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def updateFile(**kwargs):
        stub = kwargs["stub"]
        overwrite = True if re.search("<<", kwargs["options"]) else False
        filecontent = kwargs["options"].lstrip('<').lstrip()
        stub.UpdateFile(distributed_fs_pb2.UpdateRequest(
            filename=kwargs['filename'],
            filecontent=filecontent,
            overwrite=overwrite
        ))
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def deleteFile(**kwargs):
        stub = kwargs["stub"]
        stub.DeleteFile(distributed_fs_pb2.DeleteRequest(
            filename=kwargs['filename']
        ))
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def listFiles(**kwargs):
        stub = kwargs["stub"]
        resp = stub.ListFiles(distributed_fs_pb2.ListRequest())
        print("\n\n")
        for filename in resp.files:
            print(f"{filename}")
        print("\n\n")
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def restoreFile(**kwargs):
        stub = kwargs["stub"]
        stub.GrantPermissions(distributed_fs_pb2.RestoreRequest(
            filename=kwargs["filename"]
        ))
        return True

    @staticmethod
    @useDistributedFileSystemStub(serverAddress)
    def grantPermissions(**kwargs):
        stub = kwargs["stub"]
        hostname, permission = kwargs["options"].split()
        stub.GrantPermissions(distributed_fs_pb2.PermissionRequest(
            filename=kwargs["filename"], hostname=hostname,
            permission=permission
        ))
        return True


class Client:

    COMMAND_PROMPT = "distributed_fs $"

    @classmethod
    @property
    def actionSelector(cls):
        return {
            'help': ActionPerformer.printHelp,
            'create': ActionPerformer.createFile,
            'read': ActionPerformer.readFile,
            'update': ActionPerformer.updateFile,
            'delete': ActionPerformer.deleteFile,
            'restore': ActionPerformer.restoreFile,
            'list': ActionPerformer.listFiles,
            'permit': ActionPerformer.grantPermissions,
            'exit': lambda **kwargs: False
        }

    @classmethod
    def getAction(cls):
        while True:
            print(cls.COMMAND_PROMPT, end=" ")
            userInput = input()
            action = Action("Invalid")
            regex = r"^(?P<command>[a-z]+)\s*(?P<filename>[\w\-.]*)" \
                    r"(?P<options>.*)"
            match = re.search(regex, userInput)
            if not match:
                print("Invalid command!")
            else:
                action = Action(
                    match.group("command"), match.group("filename"),
                    match.group("options").strip()
                )
            yield action

    @classmethod
    def performAction(cls, action):
        operation = cls.actionSelector.get(action.command)
        if not operation:
            print("Invalid command!")
            return True
        return operation(filename=action.filename, options=action.options)

    @classmethod
    def run(cls, serverAddress):
        ActionPerformer.serverAddress = serverAddress
        print("\n\n\t---: Distributed File System :---")
        print("\n\t\tEnter help to get started ...\n\n")
        for action in cls.getAction():
            if not cls.performAction(action):
                break
