# coding:utf-8
import xmltodict
import json
import os
import random


def search_by_key(js_obj, key):
    for k in js_obj:
        if k == key:
            return js_obj[k]
        if isinstance(js_obj[k], dict):
            js = search_by_key(js_obj[k], key)
            if js:
                return js
        if isinstance(js_obj[k], list):
            for item in js_obj[k]:
                js = search_by_key(item, key)
                if js:
                    return js
    return


def transfer_vertice(src_obj):
    trg_obj = json.loads("{}")
    trg_obj["id"] = src_obj["@xmi.id"]
    if '@name' in src_obj:
        trg_obj["name"] = src_obj["@name"]
    else:
        trg_obj["name"] = "anonymous"
    if '@kind' in src_obj:
        trg_obj["kind"] = src_obj["@kind"]
    js_exit = search_by_key(src_obj, "UML:State.exit")
    if js_exit:
        trg_obj["exit"] = \
            js_exit["UML:ActionSequence"]["UML:ActionSequence.action"]["UML:CallAction"]["@name"]
    js_entry = search_by_key(src_obj, "UML:State.entry")
    if js_entry:
        trg_obj["entry"] = \
            js_entry["UML:ActionSequence"]["UML:ActionSequence.action"]["UML:CallAction"]["@name"]
    js_doActivity = search_by_key(src_obj, "UML:State.doActivity")
    if js_doActivity:
        trg_obj["doActivity"] = \
            js_doActivity["UML:ActionSequence"]["UML:ActionSequence.action"]["UML:CallAction"]["@name"]
    return trg_obj


def random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


class EaPaser:
    _xml_file = None
    _js_data = None
    _js_file = None
    _js_graph = None
    _graph_file = None

    def __init__(self, xml_file):
        self._xml_file = xml_file
        self._js_graph = json.loads("{}")
        self._js_file = self._xml_file.replace('.xmi', '.json')
        self._graph_file = self._xml_file.replace('.xmi', '_graph.json')
        self._xml2json()
        self.transform()

    def _xml2json(self):
        if os.path.exists(self._js_file):
            os.remove(self._js_file)
        with open(self._xml_file) as xml_f:
            self._js_data = xmltodict.parse(xml_f.read())
            xml_f.close()
            with open(self._js_file, 'w') as js_f:
                json.dump(self._js_data, js_f, indent=4)
                js_f.close()

    def _add_vertices(self, node_type):
        js_node = search_by_key(self._js_data, node_type)
        if js_node:
            if isinstance(js_node, list):
                for item in js_node:
                    self._js_graph["vertices"].append(transfer_vertice(item))
            if isinstance(js_node, dict):
                self._js_graph["vertices"].append(transfer_vertice(js_node))

    def _add_edges(self, edge_type):
        js_edges = search_by_key(self._js_data, edge_type)
        if js_edges:
            for item in js_edges:
                js_obj = json.loads("{}")
                js_obj["id"] = item["@xmi.id"]
                js_obj["sourceVertexId"] = item["@source"]
                js_obj["targetVertexId"] = item["@target"]
                for js_edge_tag in item["UML:ModelElement.taggedValue"]["UML:TaggedValue"]:
                    idref = js_edge_tag["UML:TaggedValue.type"]["UML:TagDefinition"]["@xmi.idref"]
                    list_TagDefinition = self._js_data["XMI"]["XMI.content"]["UML:Model"]["UML:Namespace.ownedElement"][
                        "UML:TagDefinition"]
                    for TagDefinition in list_TagDefinition:
                        if idref == TagDefinition["@xmi.id"]:
                            if TagDefinition["@name"] == "privatedata1":
                                js_obj["Call"] = js_edge_tag["UML:TaggedValue.dataValue"]
                            if TagDefinition["@name"] == "privatedata2":
                                js_obj["Guard"] = js_edge_tag["UML:TaggedValue.dataValue"]
                            if TagDefinition["@name"] == "privatedata3":
                                js_obj["Guard_Effect"] = js_edge_tag["UML:TaggedValue.dataValue"]
                self._js_graph["edges"].append(js_obj)

    def _reconstruct(self):
        vertices = self._js_graph["vertices"]
        edges = self._js_graph["edges"]
        for v in vertices:
            if "exit" in v:
                v_exit = json.loads("{}")
                v_exit["name"] = "exit"
                v_exit["id"] = "EXIT_" + random_str(10)
                v_exit["kind"] = "exit"
                v_exit["entry"] = v["exit"]
                del v["exit"]
                vertices.append(v_exit)
                e_exit = json.loads("{}")
                e_exit["id"] = "EXIT_" + random_str(10)
                e_exit["sourceVertexId"] = v["id"]
                e_exit["targetVertexId"] = v_exit["id"]
                edges.append(e_exit)

    def transform(self):
        js_model = search_by_key(self._js_data, "UML:Model")
        if js_model:
            self._js_graph["name"] = js_model["@name"]
            self._js_graph["id"] = js_model["@xmi.id"]
        self._js_graph["vertices"] = []
        self._add_vertices("UML:SimpleState")
        self._add_vertices("UML:FinalState")
        self._add_vertices("UML:Pseudostate")
        self._js_graph["edges"] = []
        self._add_edges("UML:Transition")
        self._reconstruct()
        with open(self._graph_file, 'w') as js_f:
            json.dump(self._js_graph, js_f, indent=4)
        js_f.close()

    def export_js(self):
        return self._js_data

    def export_graph(self):
        return self._js_graph


if __name__ == '__main__':
    EA_xmi_file = '../input/Demo.xmi'
    x2j = EaPaser(EA_xmi_file)
