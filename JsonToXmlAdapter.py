import json as j
import xml.etree.cElementTree as e
import xmltodict
import json


def jsonToXml(self,request):
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

    return xmlstr

def xmlToJson(self,s):
    # root = e.fromstring(s)
    data_dict = xmltodict.parse(s)
    json_data = json.dumps(data_dict)
    print(json_data)

    return json_data
