import argparse
import multiprocessing

from client import Client
from server import Server
from utils.network import isValidIpAddress


def prepareServer():

    def checkIp(ip):
        if not isValidIpAddress(ip):
            raise argparse.ArgumentTypeError(f"{ip} is not a valid ip address")
        return ip

    parser = argparse.ArgumentParser(
        description="Distributed File System Client")
    parser.add_argument("--ip", help="ip address",
                        type=checkIp, required=True)
    parser.add_argument("--port", help="port number", type=str, required=True)
    parser.add_argument("--hostname", help="Host name", default="myhost")
    args = parser.parse_args()

    server = Server(args.ip, args.port)
    return server


def main():
    server = prepareServer()
    serverProcess = multiprocessing.Process(target=server.run)
    serverProcess.start()
    Client.run()
    serverProcess.terminate()


if __name__ == '__main__':
    main()
