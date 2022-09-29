import json

tmp = {
    "a": {"@xmi": "1"},
    "a": {"@xmi": "3"},
    "b": {"@xmi": "2"}
}

def search_by_key(js_obj, key, js_res):
    for k in js_obj:
        if k == key:
            js_res.append(js_obj(k))
            return js_obj[k]
        if isinstance(js_obj[k], dict):
            search_by_key(js_obj[k], key)
        if isinstance(js_obj[k], list):
            for item in js_obj[k]:
                search_by_key(item, key)
    return



if __name__ == '__main__':
    js = json.dump("key" , "value")
    print(js)