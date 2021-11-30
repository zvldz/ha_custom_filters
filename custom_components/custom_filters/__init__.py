"""Support custom filters for jinja2 templating"""
import ast
import base64
import json
import re
import urllib.parse
import zlib

from random import Random, SystemRandom, shuffle

import logging

from homeassistant.helpers import template

_LOGGER = logging.getLogger(__name__)

_TemplateEnvironment = template.TemplateEnvironment


# --
# - DEFLATE
# --
def deflate(string):
    """Deflates/decompresses a string"""
    return zlib.decompress(string)


# --
# - INFLATE
# --
def inflate(string):
    """Inflates/compresses a string"""
    return zlib.compress(string.encode("utf-8"))


# --
# - DECODE BASE64 AND INFLATE
# --
def decode_base64_and_inflate(string):
    """Decodes and inflates a string"""
    data = base64.b64decode(string)
    return zlib.decompress(data).decode("utf-8")


# --
# - DEFLATE AND BASE64 ENCODE
# --
def deflate_and_base64_encode(string):
    """Deflates and encodes a string"""
    data = zlib.compress(string.encode("utf-8"))
    return base64.b64encode(data).decode("utf-8")


# --
# - DECODE VALETUDO MAP
# --
def decode_valetudo_map(string):
    """Currently equivalent to deflate_and_base64_encode."""
    return decode_base64_and_inflate(string)


# --
# - UNQUOTE
# --
def unquote(string):
    """Remove quotes from a string"""
    return urllib.parse.unquote(string)


# --
# - STRTOLIST
# --
def strtolist(string, delim=","):
    """Convert a string to a list"""
    obj_res = re.sub(r"([\s]?)+['\"]+([\s]?)", "",
                     string.strip((r"[]"))).strip()
    if len(obj_res) == 0:
        obj_res = []
    else:
        obj_res = obj_res.split(delim)
    return obj_res


# --
# - LISTIFY
# --
def listify(string, delim=","):
    """Convert a string or non-list/dict into a list/dict"""
    if isinstance(string, (list, dict)):
        obj_res = string
    else:
        obj_res = str(string).strip()
        # Determine if it's a dict, list, or implied list
        if obj_res.startswith('{') and obj_res.endswith('}'):
            obj_res = ast.literal_eval(obj_res)
        else:
            if not obj_res.startswith('[') and not obj_res.endswith(']'):
                obj_res = "[" + obj_res + "]"
            # Convert to list or return the dict
            if obj_res.startswith('[') and obj_res.endswith(']'):
                if obj_res == "[]":
                    obj_res = []
                else:
                    obj_res = strtolist(obj_res.replace(
                        "[ ", "[").replace(" ]", "]").replace(delim + " ", delim))
    return obj_res


# --
# - GET INDEX
# --
def get_index(obj, key, fallback=False):
    """Return the numeric index of a list or dict item"""
    # Normalize the list
    if isinstance(obj, dict):
        list_obj = list(obj.keys())
    elif isinstance(obj, list):
        list_obj = obj
    else:
        list_obj = listify(obj)
    # Check if index exists
    try:
        index_value = list_obj.index(key)
    except ValueError:
        index_value = fallback
    return index_value


# --
# - GRAB
# --
def grab(obj, key=0, fallback=""):
    """Get a list/dict item by key, with optional fallback"""
    # Normalize the object
    if isinstance(obj, str):
        obj = listify(obj)
    # Normalize the key based on object type
    if isinstance(obj, dict):
        if isinstance(key, int):
            try:
                key = obj[list(obj)[key]]
            except IndexError:
                return fallback
        elif not isinstance(key, str):
            return fallback
    elif isinstance(obj, list):
        if not isinstance(key, int):
            return fallback
    else:
        return fallback
    # Check if key/value exists
    try:
        my_val = obj[key]
    except IndexError:
        return fallback
    return my_val


# --
# - REACH
# --
def reach(obj, keypath, fallback=""):
    """Get a dict item by full path of key(s), with optional fallback"""
    res = {"found": True, "level": obj, "val": False}
    keys = keypath.split('.')
    if isinstance(obj, (dict, list)):
        for key in keys:
            if res["found"] is True:
                try:
                    res["level"] = res["level"][key]
                except KeyError:
                    res["found"] = False
                    return fallback
            else:
                return fallback
    else:
        return fallback
    return res["level"]


# --
# - TERNARY
# --
def ternary(value, true_val, false_val, none_val=None):
    """Ternary evaluation fo True, False, or None values"""
    # value ? true_val : false_val
    if value is None and none_val is not None:
        res = none_val
    elif bool(value):
        res = true_val
    else:
        res = false_val
    return res


# --
# - RANDOMIZE LIST
# --
def randomize_list(mylist, seed=None):
    """Shuffle list"""
    try:
        mylist = listify(mylist)
        if seed:
            rand = Random(seed)
            rand.shuffle(mylist)
        else:
            shuffle(mylist)
    except Exception:
        pass
    return mylist


# --
# - TO ASCII JSON
# --
def to_ascii_json(string):
    """Convert string to ASCII JSON"""
    return json.dumps(string, ensure_ascii=False)


# --
# - INIT
# --
def init(*args):
    """Initialize filters"""
    env = _TemplateEnvironment(*args)
    env.filters["unquote"] = unquote
    env.filters["strtolist"] = strtolist
    env.filters["listify"] = listify
    env.filters["get_index"] = get_index
    env.filters["grab"] = grab
    env.filters["reach"] = reach
    env.filters["urldecode"] = unquote
    env.filters["ternary"] = ternary
    env.filters["shuffle"] = randomize_list
    env.filters["deflate"] = deflate
    env.filters["inflate"] = inflate
    env.filters["deflate_and_base64_encode"] = deflate_and_base64_encode
    env.filters["decode_base64_and_inflate"] = decode_base64_and_inflate
    env.filters['to_ascii_json'] = to_ascii_json
    env.filters["decode_valetudo_map"] = decode_valetudo_map
    return env


template.TemplateEnvironment = init
template._NO_HASS_ENV.filters["unquote"] = unquote
template._NO_HASS_ENV.filters["strtolist"] = strtolist
template._NO_HASS_ENV.filters["listify"] = listify
template._NO_HASS_ENV.filters["get_index"] = get_index
template._NO_HASS_ENV.filters["grab"] = grab
template._NO_HASS_ENV.filters["reach"] = reach
template._NO_HASS_ENV.filters["urldecode"] = unquote
template._NO_HASS_ENV.filters["ternary"] = ternary
template._NO_HASS_ENV.filters["shuffle"] = randomize_list
template._NO_HASS_ENV.filters["deflate"] = deflate
template._NO_HASS_ENV.filters["inflate"] = inflate
template._NO_HASS_ENV.filters["deflate_and_base64_encode"] = deflate_and_base64_encode
template._NO_HASS_ENV.filters["decode_base64_and_inflate"] = decode_base64_and_inflate
template._NO_HASS_ENV.filters['to_ascii_json'] = to_ascii_json
template._NO_HASS_ENV.filters["decode_valetudo_map"] = decode_valetudo_map


async def async_setup(hass, hass_config):
    return True
