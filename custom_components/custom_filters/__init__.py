"""Support custom filters for jinja2 templating"""
import ast
import base64
import json
import re
import urllib.parse
import zlib
import logging
import datetime
import dateutil.parser

from random import Random, SystemRandom, shuffle

from homeassistant.helpers import template

_LOGGER = logging.getLogger(__name__)

_TemplateEnvironment = template.TemplateEnvironment


## -- REPLACE ALL
def replace_all(text, find, replace = ''):
    """Replace all provided values with replacement value(s)"""
    find_all = find if isinstance(find, (list)) else [find]
    for i in find_all:
        r = replace if not isinstance(replace, (list)) else replace[find.index(i)]
        text = text.replace(i, r)
    return text


## -- IS DEFINED
def is_defined(varname):
    """Check if a variable is defined by it's string name"""
    try:
        globals()[varname]
    except NameError:
        return False
    else:
        return True


## -- GET TYPE
def get_type(val):
    """Return the object type as a string"""
    return type(val).__name__


## -- IS TYPE
def is_type(val, typeof):
    """Check if a value is of given type"""
    if str(typeof) == typeof:
        typeof = typeof
    elif isinstance(typeof, type):
        typeof = getattr(typeof, '__name__', False)
    else:
        typeof = False
    if not isinstance(typeof, str):
        return None
    typeof = typeof.lower()
    val_type = type(val).__name__
    check_type = (typeof.lower()
        .replace('boolean', 'bool')
        .replace('integer', 'int')
        .replace('double', 'float')
        .replace('array', 'list')
        .replace('string', 'str').replace('text', 'str')
        .replace('dictionary', 'dict').replace('mapping', 'dict')
        .replace('nonetype', 'none').replace('none', 'NoneType').replace('null', 'NoneType')
    )
    if check_type == 'number':
        passchk = val_type in ['int', 'float', 'complex']
    elif check_type == 'sequence':
        passchk = val_type in ['list', 'tuple', 'range']
    elif check_type == 'json':
        passchk = val_type in ['dict', 'list']
    else:
        passchk = val_type == check_type
    return passchk


## -- INFLATE
def inflate(string):
    """Inflates/compresses a string"""
    return zlib.compress(string.encode("utf-8"))


## -- DEFLATE
def deflate(string):
    """Deflates/decompresses a string"""
    return zlib.decompress(string)


## -- DECODE BASE64 AND INFLATE
def decode_base64_and_inflate(string):
    """Decodes and inflates a string"""
    data = base64.b64decode(string)
    return zlib.decompress(data).decode("utf-8")


## -- DEFLATE AND BASE64 ENCODE
def deflate_and_base64_encode(string):
    """Deflates and encodes a string"""
    data = zlib.compress(string.encode("utf-8"))
    return base64.b64encode(data).decode("utf-8")


## -- DECODE VALETUDO MAP
def decode_valetudo_map(string):
    """Currently equivalent to deflate_and_base64_encode."""
    return decode_base64_and_inflate(string)


## -- URL DECODE
def urldecode(string):
    """Remove quotes from a string"""
    return urllib.parse.unquote(string)


## -- STRTOLIST
def strtolist(string, delim=","):
    """Convert a string to a list"""
    obj_res = re.sub(r"([\s]?)+(['\"])+([\s]?)", "\\2", string.strip((r"[]"))).strip()
    if len(obj_res) == 0:
        obj_res = []
    else:
        if delim != ",":
            obj_res = obj_res.replace(delim, ",")
        obj_res = "[" + obj_res.strip("[]") + "]"
        try:
            obj_res = ast.literal_eval(obj_res)
        except ValueError:
            obj_res = obj_res.split(",")
    return obj_res


## -- LISTIFY
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
            if not obj_res.startswith('['):
                obj_res = "[" + obj_res
            if not obj_res.endswith(']'):
                obj_res = obj_res + "]"
            # Convert to list or return the dict
            if obj_res.startswith('[') and obj_res.endswith(']'):
                if obj_res == "[]":
                    obj_res = []
                else:
                    obj_res = strtolist(obj_res.replace(
                        "[ ", "[").replace(" ]", "]").replace(delim + " ", delim))
    return obj_res


## -- GET INDEX
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


## -- GRAB
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


## -- REACH
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


## -- TERNARY
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


## -- RANDOMIZE/SHUFFLE LIST
def shuffle(mylist):
    """Shuffle list"""
    try:
        mylist = listify(mylist)
        rand = Random()
        rand.shuffle(mylist)
    except Exception:
        pass
    return mylist


## -- TO ASCII JSON
def to_ascii_json(string):
    """Convert string to ASCII JSON"""
    return json.dumps(string, ensure_ascii=False)


## -- Format Date
def get_format_date_function(format="%d %b %Y, %H:%M:%S"):
    def format_date(obj):
        if isinstance(obj, datetime.date):
            return obj.strftime(format)
        return dateutil.parser.parse(obj).strftime(format)
    return format_date

## -- String to local datetime
def as_local_datetime(string):
    env = template._NO_HASS_ENV
    return  env.filters['as_local'](env.filters['as_datetime'](string))

def debug(*args):
    return template.TemplateEnvironment().filters

# Array of functions to add as custom filters. Creates a filter and a global macro using the functions name.
# You can also supply a dict with "name" and "function" keys to specify a custom name for the filter/macro.
custom_filters = [
    replace_all, 
    is_defined, 
    get_type, 
    is_type, 
    inflate, 
    deflate, 
    decode_base64_and_inflate, 
    deflate_and_base64_encode, 
    decode_valetudo_map, 
    urldecode, 
    strtolist, 
    listify, 
    get_index, 
    grab, 
    reach, 
    ternary, 
    shuffle, 
    to_ascii_json, 
    { "name": "format_date", "function": get_format_date_function() }, 
    as_local_datetime
]

def add_custom_filter_function(custom_filter, *environments):
    name = custom_filter["name"] if isinstance(custom_filter, dict) else custom_filter.__name__
    function = custom_filter["function"] if isinstance(custom_filter, dict) else custom_filter
    for env in environments:
        env.globals[name] = env.filters[name] = function

def init(*args):
    """Initialize filters"""
    env = _TemplateEnvironment(*args)
    
    for f in custom_filters:
        add_custom_filter_function(f, env)

    return env


template.TemplateEnvironment = init
for f in custom_filters:
    add_custom_filter_function(f, template._NO_HASS_ENV)

async def async_setup(hass, hass_config):
    config = hass_config["custom_filters"]

    tpl = template.Template("", hass)
    _LOGGER.error(config)
    for f in custom_filters:
        add_custom_filter_function(f, tpl._env)

    if config["custom_date_format"]:
        add_custom_filter_function(get_format_date_function(config["custom_date_format"]), tpl._env, template._NO_HASS_ENV)
    return True
