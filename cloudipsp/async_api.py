import logging
from types import MethodType
from cloudipsp import exceptions

try:
    import aiohttp
except ImportError:
    aiohttp = False

from cloudipsp.api import BaseAPI

log = logging.getLogger(__name__)


class AsyncAPI(BaseAPI):
    is_async = True

    def __init__(self, **kwargs):
        if not aiohttp:
            raise ModuleNotFoundError(
                "Run 'pip install -U aiohttp' to work with AsyncAPI"
            )
        super().__init__(**kwargs)
