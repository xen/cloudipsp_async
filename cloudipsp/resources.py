from __future__ import absolute_import, unicode_literals
from cloudipsp import utils
from cloudipsp import exceptions
import logging
from functools import partial

log = logging.getLogger(__name__)

try:
    import aiohttp
except ImportError:
    aiohttp = False
try:
    import requests
except ImportError:
    requests = False


class Resource(object):
    def __init__(self, api=None, headers=None):
        self.__dict__["api"] = api
        self.is_async = api.is_async

        self.data = {}
        self.headers = headers or {}
        self.order_id = None

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    async def _async_call(self, api_method, params):
        path, data = api_method(params)
        log.debug("Request Type: %s", self.api.request_type)
        log.debug("URL: %s", path)
        log.debug("Data: %s", str(data))
        log.debug("Headers: %s", str(self.headers))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://{self.api.api_domain}/api{path}",
                data=data,
                headers=self.headers,
            ) as r:
                resp = await r.text()
                log.debug("Status: %s", r.status)
                log.debug("Responce: %s", resp)
                print(r.status)
                print(resp)

                if r.status in (200, 201):
                    return self.response(data)

            raise exceptions.ServiceError(f"Response code is: {resp.status}")

    def _call(self, api_method, params):
        """
        :param url: request url
        :param method: request method, POST default
        :param data: request data
        :param headers: request headers
        :return: api response
        """
        path, data = api_method(params)
        log.debug("Request Type: %s", self.request_type)
        log.debug("URL: %s", path)
        log.debug("Data: %s", str(data))
        log.debug("Headers: %s", str(self.headers))

        resp = requests.request(
            "post",
            f"https://{self.api.api_domain}/api{path}",
            data=data,
            headers=self.headers,
        )
        log.debug("Responce: %s", str(resp.content.decode("utf-8")))

        return self.response(resp.content.decode("utf-8"))

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]

        try:
            api_method = super().__getattribute__("api_" + key)
        except AttributeError:
            api_method = None

        if api_method:
            if self.is_async:
                return partial(self._async_call, api_method)
            return partial(self._call, api_method)
        return super().__getattribute__(key)

    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except AttributeError:
            self.__data__[name] = self.convert(name, value)

    def __contains__(self, name):
        return name in self.__data__

    def get_url(self):
        if "checkout_url" in self.__data__:
            return self.__getattr__("checkout_url")

    def response(self, response):
        """
        :param response: api response
        :return: result
        """
        try:
            result = None
            if self.api.request_type == "json":
                result = utils.from_json(response).get("response", "")
            if self.api.request_type == "xml":
                result = utils.from_xml(response).get("response", "")
            if self.api.request_type == "form":
                result = utils.from_form(response)
            return self._get_result(result)
        except KeyError:
            raise ValueError("Undefined format error.")

    def _get_result(self, result):
        """
        in some api param response_status not exist...
        :param result: api result
        :return: exception
        """
        if "error_message" in result:
            raise exceptions.ResponseError(result)
        if "data" in result and self.api.api_protocol == "2.0":
            result["data"] = utils.from_b64(result["data"])
        self.__data__ = result
        return result
