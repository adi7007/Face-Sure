import urllib.request
import json

res = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/openapi.json").read())
for p in sorted(res["paths"].keys()):
    print(p)
