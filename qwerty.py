#! /usr/bin/python
from socket import socket, AF_UNIX, SOCK_DGRAM
import time
import pathlib

def connect_out_socket() -> socket:
    out_socket = socket(family=AF_UNIX, type=SOCK_DGRAM)
    out_socket.connect("/tmp/qwerty.socket")
    return out_socket

def bind_in_socket() -> socket:
    in_socket = socket(family=AF_UNIX, type=SOCK_DGRAM)
    socket_path = pathlib.Path("/tmp/qwerty_anki.socket")
    if socket_path.exists():
        socket_path.unlink()
    in_socket.bind(str(socket_path))
    return in_socket

class Connection:
    def __init__(self):
        self.in_socket = bind_in_socket()
        self.out_socket = connect_out_socket()
        self.out_socket.sendall(b"start")
        
    def send_word(self, word: str):
        self.out_socket.sendall(word.encode())

    def receive_error_times(self) -> int:
        buf = self.in_socket.recv(128)
        msg = buf.decode()
        return int(msg)

def main():
    con = Connection()
    con.send_word("apple")
    i = con.receive_error_times()
    print("error times:", i)

if __name__ == "__main__":
    main()
