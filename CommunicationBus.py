import socket

IP = "127.0.0.1"
HOST_PORT = 5005
BUFFER_SIZE = 1024

host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("CommunicationBus listening for connections..")
host_socket.listen()
conn, addr = host_socket.accept()
print ('Connection address:', addr)


while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from webclient:", primljeno)
    zahtev = primljeno
    conn.send(zahtev.encode())



host_socket.close()