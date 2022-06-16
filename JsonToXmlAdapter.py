import json as j
import xml.etree.cElementTree as e
import xmltodict
import json
import socket


IP = "127.0.0.1"
HOST_PORT = 5006
BUFFER_SIZE = 1024

host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("JsonXmlAdapter listening for connections..")
host_socket.listen()



conn, addr = host_socket.accept()
print ('Connection address:', addr)


def json_to_xml(request):
    d = json.loads(request)
    print(d)

    r = e.Element("request")

    e.SubElement(r, "verb").text = d["verb"]
    e.SubElement(r, "noun").text = d["noun"]
    if "query" in d:
        e.SubElement(r, "query").text = d["query"]
    if "fields" in d:
        e.SubElement(r, "fields").text = d["fields"]


    xmlstr = e.tostring(r, encoding='utf8', method='xml')

    return xmlstr


def xml_to_json(s):
    data_dict = xmltodict.parse(s)
    json_data = json.dumps(data_dict)
    return json_data

while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from client:", primljeno)
    zahtev = primljeno
    if zahtev[0] != '<':
        data_dict = json_to_xml(zahtev)
    else :
        data_dict  = xml_to_json(zahtev)
    conn.sendall(str(data_dict).encode())