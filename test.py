import requests
import json

api_key = "nazpgms5bqejgj1fwolg1c6w"

term = input("What do you want to search Etsy for?")

def search(term):
    base_url = "https://openapi.etsy.com/v2/listings/active?"
    params_d = {}
    params_d['keywords'] = term
    params_d['api_key'] = api_key
    req = requests.get(base_url, params = params_d)
    s = json.loads(req.text)
    return len(s['results'])

print (search(term))
