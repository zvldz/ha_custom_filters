# Custom filters for jinja (Home Assistant)

## Installation
*__Manual mode__*

Place the `custom_filters` folder into your `custom_components` folder.

*__Adding custom repository to [HACS](https://hacs.xyz/)__*

Go to the Integrations page in HACS and select the three dots in the top right corner. Select Custom repositories.
Add repository url. Category - Integration. Read more on https://hacs.xyz/docs/faq/custom_repositories.

Add `custom_filters:` to your configuration.yaml.


## Filters
<p>

```
unquote                     - Replace %xx escapes by their single-character equivalent.
urldecode                   - Alias for `unqoute`
replace_all                 - Replace all provided values with replacement value(s)
                              [ e.g. `replace_all("This is a string", ["This", "a"], "--")` => "-- is -- string" ]
is_defined                  - Check if a variable is defined by it's string name (e.g. is_defined('varname'))
get_type                    - Return the object type as a string
is_type                     - Check if a value is of given type (e.g. is_type('str', 'float'))
strtolist                   - Turn a string (e.g. "['blue', 'red']") into a list
listify                     - Convert a string or non-list/dict into a list/dict
get_index                   - Return the numeric index of a list or dict item
grab                        - Get a list/dict item by key, with optional fallback
reach                       - Get a dict item by full path of key(s), with optional fallback
                              [ e.g. `reach({'a':{'b':{'c':10}}}, 'a.b.c')` => 10 ]
ternary                     - To use one value on true, one value on false and a third value on null
shuffle                     - Randomize an existing list, giving a different order every invocation
deflate                     - Decompress with zlib
inflate                     - Compress with zlib
decode_base64_and_inflate   - Decode base64 content and decompress it
deflate_and_base64_encode   - Compress content and base64 encode it
decode_valetudo_map         - Decode Valetudo (https://github.com/Hypfer/Valetudo) map
```

</p>
