import json
import copy


class PathFinder:
    _matrix = None
    _list_v = []
    _paths = json.loads("{}")

    def __init__(self, js_graph):
        for v in js_graph["vertices"]:
            self._list_v.append(v)
        # substitute edge id with edge index
        for idx, v in enumerate(self._list_v):
            for e in js_graph["edges"]:
                if v["id"] == e["sourceVertexId"]:
                    del e["sourceVertexId"]
                    e["sourceVertexId"] = idx
                if v["id"] == e["targetVertexId"]:
                    del e["targetVertexId"]
                    e["targetVertexId"] = idx
            del v["id"]
            v["id"] = idx
        list_size = len(js_graph["vertices"])
        # construct a edge matrix and filled with None.
        self._matrix = [[None for j in range(1, list_size + 1)] for i in range(1, list_size + 1)]
        for e in js_graph["edges"]:
            src_idx = -1
            dst_idx = -1
            for idx, item in enumerate(self._list_v):
                if e["sourceVertexId"] == item["id"]:
                    src_idx = idx
                if e["targetVertexId"] == item["id"]:
                    dst_idx = idx
                if src_idx != -1 and dst_idx != -1:
                    break
            self._matrix[src_idx][dst_idx] = e
        self._paths["model"] = js_graph["name"]
        self._paths["paths"] = []
        self._paths["paths"].append(list())
        self._find_paths()

    def _search_paths(self, current_path, current_idx):
        current_path.append(current_idx)
        backup_path = copy.deepcopy(current_path)
        is_fork = False
        for idx, e in enumerate(self._matrix[current_idx]):
            if e:
                if not is_fork:
                    is_fork = True
                    self._search_paths(current_path, idx)
                else:
                    fork_path = copy.deepcopy(backup_path)
                    self._paths["paths"].append(fork_path)
                    self._search_paths(fork_path, idx)

    def _find_paths(self):
        for idx, n in enumerate(self._list_v):
            if "kind" in n:
                if n["kind"] == "initial":
                    self._search_paths(self._paths["paths"][0], idx)
                    return

    def export_matrix(self):
        return self._matrix

    def export_list_v(self):
        return self._list_v

    def export_paths(self):
        return self._paths

    def export_node_names(self):
        node_names = []
        for path in self._paths["paths"]:
            node_name = []
            for v_idx in path:
                node_name.append(self._list_v[v_idx]["name"])
            node_names.append(node_name)
        return node_names


if __name__ == '__main__':
    with open("../input/Demo_graph.json", encoding='utf-8') as gf:
        js_gf = json.load(gf)
        gf.close()
    g = PathFinder(js_gf)
    print(g.export_matrix())
    print(g.export_paths())
    print(g.export_node_names())
