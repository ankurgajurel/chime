import socket
import json
from dataclasses import dataclass, asdict
from threading import Thread


@dataclass
class Request:
    command: str
    args: dict[str, str]


@dataclass
class Response:
    message: str
    heard: str


username = ""


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 3009))


def send_all(message: str):
    req = Request(command="sendAll", args={"message": message})
    req_json = json.dumps(asdict(req)) + "\n"
    client.send(req_json.encode("utf-8"))

    return "Sent: " + message


def whisper(message: str, username: str):
    req = Request(command="whisper", args={"message": message, "username": username})
    req_json = json.dumps(asdict(req)) + "\n"
    client.send(req_json.encode("utf-8"))

    return "Whispered: " + message + " to " + username


def register(new_username: str):
    req = Request(command="register", args={"username": new_username})
    req_json = json.dumps(asdict(req)) + "\n"

    global username
    username = new_username
    client.send(req_json.encode("utf-8"))

    return "Registered as " + new_username


def parse_slash_command(text: str):
    command_parts = text.split(" ")
    command = command_parts[0]

    if command.startswith("/"):
        if command == "/help":
            return "Help Command"

        elif command == "/sendall":
            if len(command_parts) > 1:
                return send_all(" ".join(command_parts[1:]))
            else:
                return "Usage: /sendall <message>"

        elif command == "/whisper":
            if len(command_parts) > 2:
                return whisper(" ".join(command_parts[1:-1]), command_parts[-1])
            else:
                return "Usage: /whisper <message> <username>"

        elif command == "/register":
            if len(command_parts) > 1:
                return register(" ".join(command_parts[1:]))
            else:
                return "Usage: /register <username>"

    return "Invalid Command"


def recv_msg(client: socket.socket, delimiter: str):
    data = ""
    while True:
        chunk = client.recv(1024).decode("utf-8")
        if not chunk:
            break
        data += chunk
        if delimiter in data:
            parts = data.split(delimiter)
            for part in parts[:-1]:
                yield part
            data = parts[-1]


def receive_messages():
    for message in recv_msg(client, "\n"):
        res_loaded = json.loads(message)
        msg_from = res_loaded["from"]
        msg = res_loaded["message"]
        print(f"\r{msg_from} > {msg}\n{username}: ", end="")
        print("\n")


Thread(target=receive_messages, daemon=True).start()

while True:
    text = input(str(username) + ": ")
    print(parse_slash_command(text))
