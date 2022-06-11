from select import select
import socket
import xml.etree.ElementTree as ET

IP = "127.0.0.1"
HOST_PORT = 5007
SERVICE_PORT = 5008
BUFFER_SIZE = 1024

class XmlDataBaseAdapter:

    def __init__(self, zahtev):
       self.zahtev = zahtev  

    #na osnovu zahteva(GET,POST,DELET ili PATCH) bira koju metodu poziva
    def ToSQL(self):
        verb = zahtev.split("verb")
        verb = verb[1][1:-2]
        get = "GET"
        post = "POST"
        delete = "DELETE"
        patch = "PATCH"        
    
        if verb in get:
            return self.MethodGetToSql()
        elif verb in delete:
            return self.MethodDeleteToSql()
        elif verb in post:
            return self.MethodPostToSql()
        elif verb in patch:
            return self.MethodPatchToSql()
        else:
            print("NE POSTOJI")
    
    zahtev =""
   
    #vraca ceo query u obliku: name='pera' AND type=1....
    def GetQuery(self):
        if("query" in zahtev):
            query = zahtev.split("query")
            query = query[1][1:len(query[1])-2]
            query = query.replace(";"," AND ")
            return query
        else:
            return False
   
    #vraca samo vredosti iz query-ja('pera' 1 ...)
    def GetValuesFromQuery(self):
        query = zahtev.split("query")
        query = query[1][1:len(query[1])-2]
        value = query.split(";")
        #value = query.split("=")
        values = list()
        for i in range(len(value)):
            temp = value[i].split("=")
            values.append(temp[1])
        
        #values = value[1:2:len(value)+1]
        return values
   
    def GetNamesFromQuery(self):
        query = zahtev.split("query")
        query = query[1][1:len(query[1])-2]
        value = query.split(";")
        #value = query.split("=")
        values = list()
        for i in range(len(value)):
            temp = value[i].split("=")
            values.append(temp[0])
        
        #values = value[1:2:len(value)+1]
        return values
    #vraca polja u obliku: id, name, surname....
    def GetFields(self):
        if("fields" in zahtev):
            fields = zahtev.split("fields")
            fields = fields[1][1:len(fields[1])-2]
            fields = fields.replace(";",", ")
            return fields
   
    #sluzi samo za PATCH jer vraca polja sa vrednostima za upload(name='pera', type=1...)
    def GetFieldsWithValues(self):
        if("fields" in zahtev):
            fields = zahtev.split("fields")
            fields = fields[1][1:len(fields[1])-2]
            fields = fields.replace(";",", ")
            return fields
        else:
            return False

    #iz zahteva dobavlja broj tabele
    def GetNumberTable(self):
        if("noun" in zahtev):
            noun = zahtev.split("noun")
            noun = noun[1].split("/")
            noun = noun[2][:-1]
            return int(noun)
    
    #na osnovu broja tabele vraca naziv tabele
    def GetStringTable(self, number):
        switcher = {
            1:"users",
            2:"user_type", 
            3:"relations",
            4:"relation_type"
        }
        return switcher.get(number,"n")
    
    #pretvara GET zahtev u sql upit
    def MethodGetToSql(self):
        sqlReq = "select "
        if(self.GetFields()):
            sqlReq += self.GetFields()+" from "
        else:
            sqlReq += "* from "
        sqlReq += self.GetStringTable(self.GetNumberTable())
        if(self.GetQuery()):
            sqlReq += " where "+self.GetQuery()
        else:
            return sqlReq
        return sqlReq

    #pretvara DELETE zahtev u sql upit
    def MethodDeleteToSql(self):
        sqlReq = "DELETE from "+self.GetStringTable(self.GetNumberTable())
        if(self.GetQuery()):
            sqlReq += " where "+ self.GetQuery()
        else:
            return sqlReq
        return sqlReq

    #pretvara POST zahtev u sql upit
    def MethodPostToSql(self):
        cnt = 0
        sqlReq = "INSERT INTO " +self.GetStringTable(self.GetNumberTable())
        
        sqlReq += "("
        for value in self.GetNamesFromQuery():
            sqlReq+=value
            cnt +=1
            if cnt == len(self.GetNamesFromQuery()):
                break
            sqlReq += ", "
        sqlReq += ") VALUES("
        
        cnt = 0
        for value in self.GetValuesFromQuery():
            cnt +=1
            sqlReq += value
            if cnt == len(self.GetValuesFromQuery()):
                break
            sqlReq += ", "
        sqlReq += ")"
        return sqlReq
    
    #pretvara PATCH zahtev u sql upit
    def MethodPatchToSql(self):
        sqlReq = "UPDATE "+self.GetStringTable(self.GetNumberTable())+ " SET "
        sqlReq += self.GetFieldsWithValues()
        if self.GetQuery():
            sqlReq += " WHERE " + self.GetQuery()
        return sqlReq

    def ToXml(self, query, result):


        rejected = "REJECTED"
        badFormat = "BAD_FORMAT"
        status_code = ["3000", "5000", "2000"]

        xmlOdgRejected = "<odgovor><status>REJECTED</status><statuscode>3000</statuscode><payload>"
        xmlOdgRejected = xmlOdgRejected  + result + "</payload></odgovor> "

        xmlOdgBadFormat = "<odgovor><status>BAD_FORMAT</status><statuscode>5000</statuscode><payload>"
        xmlOdgBadFormat = xmlOdgBadFormat  + result + "</payload></odgovor>"

        if result == "R E J E C T E D":
            return xmlOdgRejected
        if result == "B A D   F O R M A T":
            return xmlOdgBadFormat

        xmlOdgsuccess = "<odgovor><status>SUCCESS</status><statuscode>2000</statuscode>"

        if "select" in query:
            odg = result.split(" ")  # od stringa koji je dosao iz repository se pravi lista
            pyl = self.ToPayloadSelect(odg, query)  # ovde se dobija payload

        elif "DELETE" in query:
            pyl = "SUCCESSFULLY DELETED"

        elif "INSERT INTO" in query:
            pyl = "SUCCESSFULLY INSERTED"

        elif "UPDATE" in query:
            pyl = "SUCCESSFULLY UPDATED"

        payload = "<payload>"+pyl+"</payload>"

        rez = xmlOdgsuccess + payload + "</odgovor>"

        return rez

    def ToPayloadSelect(self, result, query):

        payload = ""
        validFields = ["id", "name", "surname", "opis", "type", "naziv", "first_user_id", "second_user_id", "tip_id"]

        start = query.find('select') + 7
        end = query.find(' from', start)
        pom = query[start:end]

        if "*" in pom:
            if "from users" in query:
                pom = "id,  name,  surname,  opis,  type"
            elif "from user_type" in query:
                pom = "id,  naziv"
            elif "from relations" in query:
                pom = "id,  first_user_id,  second_user_id,  tip_id"
            elif "from relation_type" in query:
                pom = "id,  naziv"

        fields = pom.split(","+"  ") #niz polja koja se kupe iz baze

        duzina = len(fields)#koliko ima clanova niz fielda
        j = 0

        #u ovim petljama se pravi payload tj xml odgovor iz baze
        while j<len(result):
            i=0
            payload = payload + '<resurs>'
            while i < duzina:
                payload = payload + '<' + fields[i] + '>' + result[j] + '</' + fields[i] + '>'
                j = j+1
                i = i+1
            payload = payload + "</resurs>"
        return payload


host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_socket.bind((IP, HOST_PORT))
print("XmlDataBaseAdapter listening for connections..")
host_socket.listen()

conn, addr = host_socket.accept()
print ('Connection address:', addr)

repository_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
repository_client_socket.connect((IP, SERVICE_PORT))

while True:
    primljeno = conn.recv(BUFFER_SIZE).decode()
    if not primljeno: break
    print ("Received data from client:", primljeno)
    zahtev = primljeno
    db1 = XmlDataBaseAdapter(zahtev)
    zahtev = db1.ToSQL()
    repository_client_socket.send(zahtev.encode())
    odgovor = repository_client_socket.recv(BUFFER_SIZE).decode()
    conn.sendall(db1.ToXml(zahtev,odgovor).encode())
    print(odgovor)


    

