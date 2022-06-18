import sys
sys.path.append("..")
import unittest
from XmlDataBaseAdapter import to_sql


class test_xml_data_base_adapter(unittest.TestCase):
    def test_get(self):
        zahtev1="<request><verb>GET</verb><noun>/resurs/1</noun><query>name='pera';type=1</query><fields>id; name; surname</fields></request>"
        self.assertEqual(to_sql(zahtev1) , "SELECT id, name, surname FROM users WHERE name='pera' AND type=1")

    def test_delete(self):
        zahtev1="<request><verb>DELETE</verb><noun>/resurs/1</noun><query>name='pera';type=1</query></request>"
        self.assertEqual(to_sql(zahtev1) , "DELETE FROM users WHERE name='pera' AND type=1")
   
   
    def test_patch(self):
        zahtev1="<request><verb>PATCH</verb><noun>/resurs/1</noun><query>name='pera';type=1</query><fields>id=2; name='zika'; surname='maric'</fields></request>"
        self.assertEqual(to_sql(zahtev1) , "UPDATE users SET id=2, name='zika', surname='maric' WHERE name='pera' AND type=1")
   
   
    def test_post(self):
        zahtev1="<request><verb>POST</verb><noun>/resurs/1</noun><query>name='pera';type=1</query></request>"
        self.assertEqual(to_sql(zahtev1) , "INSERT INTO users(name, type) VALUES('pera', 1)")

    def test_get_all(self):
        zahtev1="<request><verb>GET</verb><noun>/resurs/1</noun></request>"
        self.assertEqual(to_sql(zahtev1) , "SELECT * FROM users")

    def test_delete_all(self):
        zahtev1="<request><verb>DELETE</verb><noun>/resurs/1</noun></request>"
        self.assertEqual(to_sql(zahtev1) , "DELETE FROM users")
    
if __name__ == "__main__":
    unittest.main()