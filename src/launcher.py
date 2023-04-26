from utils.network import isValidIpAddress
from utils import constants

import argparse
import multiprocessing


def parseArgs():
    def checkIp(ip):
        if not isValidIpAddress(ip):
            raise argparse.ArgumentTypeError(f"{ip} is not a valid ip address")
        return ip

    parser = argparse.ArgumentParser(
        description="Distributed File System Client")
    parser.add_argument("--ip", help="ip address",
                        type=checkIp, required=True)
    parser.add_argument("--port", help="port number", type=str, required=True)
    parser.add_argument("--hostname", help="Host name",
                        type=str, required=True)
    return parser.parse_args()

    return server


def main():
    args = parseArgs()
    # TODO: Handle these global constants better
    constants.setupGlobalConstants(
        ":".join((args.ip, args.port)), args.hostname
    )

    # Lauch server
    from server import Server  # Do not changet this import
    serverObj = Server(args.ip, args.port, args.hostname)
    serverProcess = multiprocessing.Process(target=serverObj.run)
    serverProcess.start()

    # Lauch Client
    from client import Client  # Do not changet this import
    Client.run()

    # Stop Server
    serverProcess.terminate()


if __name__ == '__main__':
    main()
