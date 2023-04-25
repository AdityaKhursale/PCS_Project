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


class Operations:
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
            grant permissions   <TODO: Update me>
            exit client         exit
        """
        print(helpMenu)
        return True

    # TODO: Check if server selection needs to be external and update
    @staticmethod
    @useDistributedFileSystemStub("localhost:50051")
    def createFile(**kwargs):
        stub = kwargs["stub"]
        stub.CreateFile(distributed_fs_pb2.CreateRequest(
            filename=kwargs['filename']))

    @staticmethod
    def readFile(**kwargs):
        pass

    @staticmethod
    def updateFile(**kwargs):
        # TODO: Decide if write and append API should be separate
        pass

    @staticmethod
    def deleteFile(**kwargs):
        pass

    @staticmethod
    def grantPermissions(**kwargs):
        # TODO: Update method once figured out exact action syntax
        pass


class Client:

    COMMAND_PROMPT = "distributed_fs $"

    @classmethod
    @property
    def actionSelector(cls):
        # TODO: Add grant permissions in below dict
        return {
            'help': Operations.printHelp,
            'create': Operations.createFile,
            'read': Operations.readFile,
            'update': Operations.updateFile,
            'delete': Operations.deleteFile,
            'exit': lambda **kwargs: False
        }

    @classmethod
    def getAction(cls):
        while True:
            print(cls.COMMAND_PROMPT, end=" ")
            userInput = input()
            action = Action("Invalid")
            regex = r"^(?P<command>[a-z]+)\s*(?P<filename>[\w\-. ]*)" \
                    r"(?P<options>.*)"
            match = re.search(regex, userInput)
            if not match:
                print("Invalid command!")
            else:
                action = Action(
                    match.group("command"), match.group("filename"),
                    match.group("options")
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
    def run(cls):
        print("\n\n\t---: Distributed File System :---")
        print("\n\t\tEnter help to get started ...\n\n")
        for action in cls.getAction():
            if not cls.performAction(action):
                break
