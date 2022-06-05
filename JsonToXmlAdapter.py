import json as j
import xml.etree.cElementTree as e
import xmltodict
import json
import socket
poruka = """{
 "verb": "GET",
 "noun": "/resurs/1",
 "query": "name='pera'; type=1",
 "fields": "id; name; surname"
}"""

IP = "127.0.0.1"
HOST_PORT = 5006
BUFFER_SIZE = 1024

host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("JsonXmlAdapter listening for connections..")
host_socket.listen()



conn, addr = host_socket.accept()
print ('Connection address:', addr)

while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from client:", primljeno)
    zahtev = primljeno

def jsonToXml(request):
    d = json.loads(request)
    print(d)

    r = e.Element("request")

    e.SubElement(r, "verb").text = d["verb"]
    e.SubElement(r, "noun").text = d["noun"]
    e.SubElement(r, "query").text = d["query"]
    e.SubElement(r, "fields").text = d["fields"]

    a = e.ElementTree(r)

    xmlstr = e.tostring(r, encoding='utf8', method='xml')

    print(xmlstr)


def xmlToJson(self,s):
    #root = e.fromstring(s)
    data_dict = xmltodict.parse(s)
    json_data = json.dumps(data_dict)
    print(json_data)

