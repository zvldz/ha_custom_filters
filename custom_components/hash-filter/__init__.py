"""Support custom filters for jinja2 templating"""
import logging
import hashlib

from homeassistant.helpers import template


_LOGGER = logging.getLogger(__name__)

_TemplateEnvironment = template.TemplateEnvironment


## -- MD5
def md5(string):
    """Convert string to MD5 checksum"""
    return hashlib.md5(string)


def init(*args):
    """Initialize filters"""
    env = _TemplateEnvironment(*args)
    env.globals["md5"] = md5
    return env


template.TemplateEnvironment = init
template._NO_HASS_ENV.globals["md5"] = md5


async def async_setup(hass, hass_config):
    tpl = template.Template("", template._NO_HASS_ENV.hass)
    tpl._env.globals = md5
    return True
