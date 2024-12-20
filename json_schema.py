"""
Generates a type schema for a dict (most commonly, use this for grokking complex json objects like when web scraping.)
"""

import json
import argparse


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", nargs="?", help="Path to the JSON file")
    args = parser.parse_args()
    if args.json_file:
        with open(args.json_file, "r") as f:
            json_data = json.loads(f.read())
    else:  # Or we just show an example
        with open("toc.json", "r") as f:
            json_data = json.loads(f.read())
    schema = extract_schema(json_data, verbose=True)
    _ = schema  # dump the value since main is for CLI usage, i.e. user just wants to see the print


if __name__ == "__main__":
    main()
