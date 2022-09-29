import json
import Parse
import FindPaths


def make_js_obj(key, value):
    js_obj = json.loads("{}")
    js_obj[key] = value
    return js_obj


def add_steps(list_step, v, e, index):
    list_step.append(make_js_obj("state", v["name"]))
    if "entry" in v:
        list_step.append(make_js_obj("entry", v["entry"]))
    if "doActivity" in v:
        list_step.append(make_js_obj("doActivity", v["doActivity"]))
    if "verify" in v:
        list_step.append(make_js_obj("verify", v["Call"]))
    if e:
        if "Guard" in e:
            js_obj = json.loads("{}")
            js_obj["Guard"] = json.loads("{}")
            js_obj["Guard"]["condition"] = e["Guard"]
            js_obj["Guard"]["if"] = json.loads("{}")
            js_obj["Guard"]["if"]["action"] = e["Guard_Effect"]
            js_obj["Guard"]["if"]["arguments"] = 0
            js_obj["Guard"]["else"] = json.loads("{}")
            js_obj["Guard"]["else"]["action"] = "wait"
            js_obj["Guard"]["else"]["arguments"] = []
            js_obj["Guard"]["else"]["arguments"].append(10)
            list_step.append(js_obj)
        if "Call" in e:
            list_step.append(make_js_obj("action", e["Call"]))


class Generator:
    _path_finder = None
    _cases = None

    def __init__(self, path_finder):
        self._path_finder = path_finder
        self._cases = json.loads("{}")
        self._cases["model"] = path_finder.export_paths()["model"]
        self._cases["cases"] = []
        self._generate()

    def _generate(self):
        list_v = self._path_finder.export_list_v()
        matrix = self._path_finder.export_matrix()
        list_p = self._path_finder.export_paths()["paths"]
        for path in list_p:
            case = json.loads("{}")
            case["name"] = ""
            case["description"] = ""
            list_step = []
            for index, v_idx in enumerate(path):
                e = None
                if index != len(path) - 1:
                    e = matrix[path[index]][path[index + 1]]
                add_steps(list_step, list_v[v_idx], e, index)
            case["steps"] = list_step
            self._cases["cases"].append(case)

    def export_cases(self):
        return self._cases


if __name__ == '__main__':
    EA_xmi_file = '../input/Demo.xmi'
    js = Parse.EA2JSON(EA_xmi_file)
    g = FindPaths.PathFinder(js.export_graph())
    cases = Generator(g)
    case_file = EA_xmi_file.replace(".xmi", "_cases.json")
    with open(case_file, "w") as f:
        json.dump(cases.export_cases(), f, indent=4)
        f.close()
