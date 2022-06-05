import socket
import json
from re import split

verb_format = ["GET", "POST", "PATCH","DELETE"]
noun_format = ["resurs","resurs_type"]
query_fields = ["id","name","surname","type",""]

IP = "127.0.0.1"
HOST_PORT = 5005
SERVICE_PORT_XMLADAPTER = 5006
BUFFER_SIZE = 1024

host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("CommunicationBus listening for connections..")
host_socket.listen()
conn, addr = host_socket.accept()
print ('Connection address:', addr)
xml_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
xml_client_socket.connect((IP, SERVICE_PORT_XMLADAPTER))

def ProveraQuery():
    query_statements=split("; ",zahtev_dict["query"])
    i=0
    query_statement=[]

    while i<len(query_statements):
        query_statement.append(split("=",query_statements[i]))
        i+=1
    for field in query_statement:
        for j in range(len(field)):
            if(j%2==0 and (field[j] not in query_fields)):
                return False
            elif (field[j]=="name" or field[j]=="surname") and "'" not in field[j+1]:
                return False
            elif (field[j]=="id" or field[j]=="type") and not field[j+1].isdigit():
                return False
    return True
def ProveraNoun():
    noun = split("/",zahtev_dict["noun"])
    noun.remove('')
    if noun[0] not in noun_format:
        return False
    if not noun[1].isdigit():
        return False
    return True
def ProveraFormata():
        
    fields=split("; ",zahtev_dict["fields"])
    
    if zahtev_dict["verb"] not in verb_format:
        return False
    if  not(ProveraNoun() and ProveraQuery()):
        return False
    for f in fields:
        if f not in query_fields:
            return False
    return True
        
    
while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from webclient:", primljeno)
    zahtev = primljeno
    zahtev_dict=json.loads(zahtev)
    provera=ProveraFormata()
    if provera == True:
        xml_client_socket.send(zahtev.encode())
        XMLzahtev = xml_client_socket.recv(BUFFER_SIZE)
        print(XMLzahtev)
    else:
        conn.send(provera.encode())





host_socket.close()