import socket
import json
import re

verb_format = ["GET", "POST", "PATCH","DELETE"]
noun_format = ["/resurs/1","/resurs/2","/resurs/3","/resurs/4"]

query_fields1 = ["id","name","surname","description","type",""]
query_fields2 = ["id","naziv",""]
query_fields3 = ["id","idFirstUser","idSecondUser","type",""]
query_fields4 = ["id","naziv",""]



IP = "127.0.0.1"
HOST_PORT = 5005
SERVICE_PORT_XMLADAPTER = 5006
SERVICE_PORT_DATABASE_ADAPTER = 5007
BUFFER_SIZE = 1024

host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("CommunicationBus listening for connections..")
host_socket.listen()
conn, addr = host_socket.accept()
print ('Connection address:', addr)

xml_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
xml_client_socket.connect((IP, SERVICE_PORT_XMLADAPTER))

sql_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sql_client_socket.connect((IP, SERVICE_PORT_DATABASE_ADAPTER))

def ProveraVerb():
    if "verb" not in zahtev_dict:
        return False
    return zahtev_dict["verb"] in verb_format

def ProveraNoun():
    if "noun" not in zahtev_dict:
        return False
    return zahtev_dict["noun"] in noun_format

def ProveraQuery():
    if "query" not in zahtev_dict:
        return False
    noun = zahtev_dict["noun"]
    
    if noun[-1] == '1':
        query_fields = query_fields1
    if noun[-1] == '2':
        query_fields = query_fields2
    if noun[-1] == '3':
        query_fields = query_fields3
    if noun[-1] == '4':
        query_fields = query_fields4

    query_statement = re.split("=|; ",zahtev_dict["query"])
    for field in query_statement:
        for j in range(len(query_statement)):
            if(j%2==0 and (query_statement[j] not in query_fields)):
                return False
            
    return True

def ProveraFields():
    if "fields" not in zahtev_dict:
        return False
    noun = zahtev_dict["noun"]
    
    if noun[-1] == '1':
        fields = query_fields1
    if noun[-1] == '2':
        fields = query_fields2
    if noun[-1] == '3':
        fields = query_fields3
    if noun[-1] == '4':
        fields = query_fields4

    if zahtev_dict["verb"] == "PATCH":
        field_statement = re.split("=|; ",zahtev_dict["fields"])
        for field in field_statement:
            for j in range(len(field_statement)):    
                if(j%2==0 and (field_statement[j] not in fields)):
                    return False
    else:
        field_statement = re.split("; ",zahtev_dict["fields"])
        for field in field_statement:
            if(field not in fields):
                return False
    
    return True


def ProveraFormata():
    if not (ProveraVerb() and ProveraNoun()):
        return False
    
    # Provera za GET
    if zahtev_dict["verb"] == "GET":
        if "query" in zahtev_dict:
            if not ProveraQuery():
                return False
        if "fields" in zahtev_dict:
            if not ProveraFields():
                return False

    # Provera za DELETE
    if zahtev_dict["verb"] == "DELETE":
        if not ProveraQuery():
            return False
    
    # Provera za POST
    if zahtev_dict["verb"] == "POST":
        if not ProveraQuery():
            return False
    
    # Provera za PATCH
    if zahtev_dict["verb"] == "PATCH":
        if not ProveraQuery():
            return False
        if not ProveraFields():
            return False
    
    return True
        
    
while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from webclient:", primljeno)
    zahtev = primljeno
    
    try:
        zahtev_dict=json.loads(zahtev)
    except:
        conn.send("BAD FORMAT".encode())
        continue
    
    provera=ProveraFormata()
    if provera == True:
        xml_client_socket.send(zahtev.encode())
        XMLzahtev = xml_client_socket.recv(BUFFER_SIZE).decode()
        sql_client_socket.send(XMLzahtev.encode())
        odgovor = sql_client_socket.recv(BUFFER_SIZE).decode()
        xml_client_socket.send(odgovor.encode())
        odgovor = xml_client_socket.recv(BUFFER_SIZE).decode()
        conn.sendall(odgovor.encode())
    else:
        conn.send('{"odgovor": {"status": "BAD_FORMAT", "statuscode": "5000", "payload": "B A D   F O R M A T"}}'.encode())





host_socket.close()
