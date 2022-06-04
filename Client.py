import json
import socket

IP = "127.0.0.1"
SERVICE_PORT = 5004
BUFFER_SIZE = 1024

f = open ('zahtevi.json', "r")
data = json.loads(f.read())
f.close()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, SERVICE_PORT))

for i in data:
    #json.dumps formatira u json, inace se zamene " sa ' pri citanju iz fajla
    zahtev = json.dumps(i)
    client_socket.send(zahtev.encode())
    rezultat = client_socket.recv(BUFFER_SIZE)
    print(rezultat.decode())


client_socket.close()
