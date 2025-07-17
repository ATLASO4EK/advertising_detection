import json
import ast

def str_to_dict(s):
    try:
        return json.loads(s)
    except Exception:
        return ast.literal_eval(s)