import argparse
import socketserver


class RequestHandler(socketserver.BaseRequestHandler):
    pass


def getArgs():
    parser = argparse.ArgumentParser(
        description="Client to interact with Distributed File System")
    parser.add_argument("--port", type=int, help="Port to listen on")
    return parser.parse_args()


def main():
    args = getArgs()
    server = socketserver.TCPServer(("localhost", args.port), RequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
