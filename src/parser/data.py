import json
from pprint import pprint

from models import Transfer

with open("data.json") as f:
    data = json.load(f)


transfer = Transfer(**data)
pprint(data)

pprint(transfer)
