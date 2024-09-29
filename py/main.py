import socket
import json
from dataclasses import dataclass, asdict


@dataclass
class Request:
    command: str
    args: dict[str, str]


@dataclass
class Response:
    message: str
    heard: str


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("localhost", 3009))

def parseSlashCommand(command: str):
    pass


def recv_msg(client: socket.socket, delimeter: str) -> str:
    data = b""
    while True:
        chunk = client.recv(1024)
        if not chunk:
            break
        data += chunk
        if data.decode("utf-8")[-1] == delimeter:
            return data.decode("utf-8")


while True:
    text = input()
    req = Request(command=text, args={})
    req_json = json.dumps(asdict(req)) + "\n"

    client.send(req_json.encode("utf-8"))
    res = recv_msg(client, "\n")

    res_loaded = json.loads(res)

    print(res_loaded)
