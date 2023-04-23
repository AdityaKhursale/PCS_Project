# import grpc
import re

# from distributed_fs import distributed_fs_pb2
# from distributed_fs import distributed_fs_pb2_grpc

# TODO: Use better naming


class Action:
    def __init__(self, command, filename=None, options=None):
        self.command = command
        self.filename = filename
        self.options = options


class Operations:
    @staticmethod
    def printHelp(**kwargs):
        help = """
            print help          help
            create file         create <filename>
            read file           read <filename>
            write to file       update <filename> < "text"
            append to file      update <filename> << "text"
            delete file         delete <filename>
            grant permissions   <TODO: Update me>
            exit client         exit
        """
        print(help)

    @staticmethod
    def createFile(**kwargs):
        pass

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
            'exit': lambda **kwargs: exit(0)
        }

    @classmethod
    def getAction(cls):
        userInput = input()
        regex = r"^(?P<command>[a-z]+)\s*(?P<filename>[\w\-. ]*)(?P<options>.*)"
        match = re.search(regex, userInput)
        if not match:
            print("Invalid command!")
            return
        return Action(
            match.group("command"), match.group("filename"),
            match.group("options")
        )

    @classmethod
    def performAction(cls, action):
        operation = cls.actionSelector.get(action.command)
        if not operation:
            print("Invalid command!")
            return
        operation(filename=action.filename, options=action.options)

    @classmethod
    def run(cls):
        print("\n\n\t---: Distributed File System :---")
        print("\n\t\tEnter help to get started ...\n\n")
        while True:
            print(cls.COMMAND_PROMPT, end=" ")
            action = cls.getAction()
            if action:
                cls.performAction(action)

        # with grpc.insecure_channel('localhost:50051') as channel:
        #     stub = distributed_fs_pb2_grpc.DistributedFileSystemStub(channel)
        #     stub.ReadFile(distributed_fs_pb2.ReadRequest())


if __name__ == '__main__':
    Client.run()
