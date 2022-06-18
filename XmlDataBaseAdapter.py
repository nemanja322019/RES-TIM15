from select import select
import socket
import xml.etree.ElementTree as ET


class XmlDataBaseAdapter:

    def __init__(self, zahtev):
       self.zahtev = zahtev  

    #na osnovu zahteva(GET,POST,DELET ili PATCH) bira koju metodu poziva
    def to_sql(self):
        verb = zahtev.split("verb")
        verb = verb[1][1:-2]
        get = "GET"
        post = "POST"
        delete = "DELETE"
        patch = "PATCH"        
    
        if verb in get:
            return self.method_get_to_sql()
        elif verb in delete:
            return self.method_delete_to_sql()
        elif verb in post:
            return self.method_post_to_sql()
        elif verb in patch:
            return self.method_patch_to_sql()
        else:
            print("NE POSTOJI")
    
    zahtev =""
   
    #vraca ceo query u obliku: name='pera' AND type=1....
    def get_query(self):
        if("query" in zahtev):
            query = zahtev.split("query")
            query = query[1][1:len(query[1])-2]
            query = query.replace(";"," AND ")
            return query
        else:
            return False
   
    #vraca samo vredosti iz query-ja('pera' 1 ...)
    def get_values_from_query(self):
        query = zahtev.split("query")
        query = query[1][1:len(query[1])-2]
        value = query.split(";")
        
        values = list()
        for i in range(len(value)):
            temp = value[i].split("=")
            values.append(temp[1])
        
        
        return values
   
    def get_names_from_query(self):
        query = zahtev.split("query")
        query = query[1][1:len(query[1])-2]
        value = query.split(";")
        
        values = list()
        for i in range(len(value)):
            temp = value[i].split("=")
            values.append(temp[0])
        

        return values
    #vraca polja u obliku: id, name, surname....
    def get_fields(self):
        if("fields" in zahtev):
            fields = zahtev.split("fields")
            fields = fields[1][1:len(fields[1])-2]
            fields = fields.replace(";",", ")
            return fields
   
    #sluzi samo za PATCH jer vraca polja sa vrednostima za upload(name='pera', type=1...)
    def get_fields_with_values(self):
        if("fields" in zahtev):
            fields = zahtev.split("fields")
            fields = fields[1][1:len(fields[1])-2]
            fields = fields.replace(";",", ")
            return fields
        else:
            return False

    #iz zahteva dobavlja broj tabele
    def get_number_table(self):
        if("noun" in zahtev):
            noun = zahtev.split("noun")
            noun = noun[1].split("/")
            noun = noun[2][:-1]
            return int(noun)
    
    #na osnovu broja tabele vraca naziv tabele
    def get_string_table(self, number):
        switcher = {
            1:"users",
            2:"user_type", 
            3:"relations",
            4:"relation_type"
        }
        return switcher.get(number,"n")
    
    #pretvara GET zahtev u sql upit
    def method_get_to_sql(self):
        sqlreq = "select "
        if(self.get_fields()):
            sqlreq += self.get_fields()+" from "
        else:
            sqlreq += "* from "
        sqlreq += self.get_string_table(self.get_number_table())
        if(self.get_query()):
            sqlreq += " where "+self.get_query()
        else:
            return sqlreq
        return sqlreq

    #pretvara DELETE zahtev u sql upit
    def method_delete_to_sql(self):
        sqlreq = "DELETE from "+self.get_string_table(self.get_number_table())
        if(self.get_query()):
            sqlreq += " where "+ self.get_query()
        else:
            return sqlreq
        return sqlreq

    #pretvara POST zahtev u sql upit
    def method_post_to_sql(self):
        cnt = 0
        sqlreq = "INSERT INTO " +self.get_string_table(self.get_number_table())
        
        sqlreq += "("
        for value in self.get_names_from_query():
            sqlreq+=value
            cnt +=1
            if cnt == len(self.get_names_from_query()):
                break
            sqlreq += ", "
        sqlreq += ") VALUES("
        
        cnt = 0
        for value in self.get_values_from_query():
            cnt +=1
            sqlreq += value
            if cnt == len(self.get_values_from_query()):
                break
            sqlreq += ", "
        sqlreq += ")"
        return sqlreq
    
    #pretvara PATCH zahtev u sql upit
    def method_patch_to_sql(self):
        sqlreq = "UPDATE "+self.get_string_table(self.get_number_table())+ " SET "
        sqlreq += self.get_fields_with_values()
        if self.get_query():
            sqlreq += " WHERE " + self.get_query()
        return sqlreq

    def to_xml(self, query, result):

        xmlodgrejected = "<odgovor><status>REJECTED</status><statuscode>3000</statuscode><payload>"
        xmlodgrejected = xmlodgrejected  + result + "</payload></odgovor> "

        xmlodgbadformat = "<odgovor><status>BAD_FORMAT</status><statuscode>5000</statuscode><payload>"
        xmlodgbadformat = xmlodgbadformat  + result + "</payload></odgovor>"

        if result == "R E J E C T E D":
            return xmlodgrejected
        if result == "B A D   F O R M A T":
            return xmlodgbadformat

        xmlodgsuccess = "<odgovor><status>SUCCESS</status><statuscode>2000</statuscode>"

        if "select" in query:
            if result == "EMPTY":
                pyl="NO SUCH RESOURCE"
            else:
                odg = result.split(" ")  # od stringa koji je dosao iz repository se pravi lista
                pyl = self.to_payload_select(odg, query)  # ovde se dobija payload

        elif "DELETE" in query:
            pyl = "SUCCESSFULLY DELETED"

        elif "INSERT INTO" in query:
            pyl = "SUCCESSFULLY INSERTED"

        elif "UPDATE" in query:
            pyl = "SUCCESSFULLY UPDATED"

        payload = "<payload>"+pyl+"</payload>"

        rez = xmlodgsuccess + payload + "</odgovor>"

        return rez

    def to_payload_select(self, result, query):

        payload = ""

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

if __name__ == "__main__":

    IP = "127.0.0.1"
    HOST_PORT = 5007
    SERVICE_PORT = 5008
    BUFFER_SIZE = 1024

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
        zahtev = db1.to_sql()
        repository_client_socket.send(zahtev.encode())
        odgovor = repository_client_socket.recv(BUFFER_SIZE).decode()
        conn.sendall(db1.to_xml(zahtev,odgovor).encode())
        print(odgovor)


    

