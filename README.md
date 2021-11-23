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
unquote                     - replace %xx escapes by their single-character equivalent.
urldecode                   - alias for `unqoute`
strtolist                   - turn a string (e.g. "['blue', 'red']") into a list
listify                     - Convert a string or non-list/dict into a list/dict
get_index                   - Return the numeric index of a list or dict item
grab                        - Get a list/dict item by key, with optional fallback
ternary                     - to use one value on true, one value on false and a third value on null
shuffle                     - randomize an existing list, giving a different order every invocation
deflate                     - zlib decompress
inflate                     - zlib compress
decode_base64_and_inflate   - decode base64 content and decompress it
deflate_and_base64_encode   - compress content and base64 encode it
decode_valetudo_map         - decode Valetudo(https://github.com/Hypfer/Valetudo) map
```

</p>
