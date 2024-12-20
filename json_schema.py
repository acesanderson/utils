"""
Generates a type schema for a dict (most commonly, use this for grokking complex json objects like when web scraping.)
"""

import json


def extract_schema(obj_to_scan, verbose=False):
    def recurse_through_object(obj):
        if isinstance(obj, dict):
            return {key: extract_schema(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [extract_schema(obj[0])] if obj else []
        else:
            return type(obj).__name__

    schema = recurse_through_object(obj_to_scan)
    if verbose:
        print(json.dumps(schema, indent=2))
    return schema


example_json = {
    "name": "John",
    "address": {"city": "NY", "street": "main", "number": 20},
    "cars": ["mazda", "nissan", "toyota"],
}

with open("toc.json", "r") as f:
    toc_json = json.loads(f.read())

schema = extract_schema(toc_json, verbose=True)
