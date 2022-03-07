#! /usr/bin/python
from socket import socket, AF_UNIX, SOCK_DGRAM
import time
import pathlib


def connect_socket() -> socket:
    sock = socket(family=AF_UNIX, type=SOCK_DGRAM)
    sock.connect("/tmp/qwerty.socket")
    return sock


def bind_socket(sock: socket):
    socket_path = pathlib.Path("/tmp/qwerty_anki.socket")
    if socket_path.exists():
        socket_path.unlink()
    sock.bind(str(socket_path))


class Connection:
    def __init__(self):
        sock = None
        try:
            sock = connect_socket()
            bind_socket(sock)
            sock.sendall(b"/start/")
            self.sock = sock
        except ConnectionRefusedError as e:
            if sock is not None:
                sock.close()
            raise e

    def send_word(self, word: str):
        self.sock.sendall(word.encode())

    def receive_error_times(self) -> int:
        buf = self.sock.recv(128)
        msg = buf.decode()
        return int(msg)

    def close(self):
        try:
            self.sock.sendall(b"/exit/")
            self.sock.close()
        except OSError:
            pass


def main():
    con = Connection()
    con.send_word("apple")
    i = con.receive_error_times()
    print("error times:", i)


if __name__ == "__main__":
    main()
