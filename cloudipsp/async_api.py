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

    async def _request(self, url, method, data, headers):
        """
        :param url: request url
        :param method: request method, POST default
        :param data: request data
        :param headers: request headers
        :return: api response
        """
        log.debug("Request Type: %s" % self.request_type)
        log.debug("URL: %s" % url)
        log.debug("Data: %s" % str(data))
        log.debug("Headers: %s" % str(headers))

        async with aiohttp.ClientSession() as session:
            caller = getattr(session, method.lower(), None)
            if not caller:
                raise NameError(f"{method} not available")

            async with caller(url, data=data, headers=headers) as resp:
                data = await resp.text()
                log.debug(f"Status: {resp.status}")
                log.debug(f"Content: {data}")

                if resp.status in (200, 201):
                    return data

            raise exceptions.ServiceError(f"Response code is: {resp.status}")
