import os

from cloudipsp.configuration import __api_url__, __protocol__, __r_type__
from cloudipsp import exceptions

try:
    import requests
except ImportError:
    requests = False

import logging
import cloudipsp.helpers as helper
import cloudipsp.utils as utils

log = logging.getLogger(__name__)


class BaseAPI(object):

    user_agent = "Python SDK"

    def __init__(self, **kwargs):
        """
        :param kwargs: args
        :arg merchant_id Merchant id numeric
        :arg secret_key Secret key string
        :arg request_type request type allowed json, xml, form
        :arg api_domain api domain
        :arg api_protocol allowed protocols 1.0, 2.0
        """

        self.merchant_id = kwargs.get("merchant_id", "")
        self.secret_key = kwargs.get("secret_key", "")
        self.request_type = kwargs.get("request_type", __r_type__)
        if not self.merchant_id or not self.secret_key:
            self.merchant_id = os.environ.get("CLOUDIPSP_MERCHANT_ID", "")
            self.secret_key = os.environ.get("CLOUDIPSP_SECRETKEY", "")
        self.api_domain = domain = kwargs.get("api_domain", "api.fondy.eu")
        self.api_url = __api_url__.format(api_domain=domain)
        self.api_protocol = kwargs.get("api_protocol", __protocol__)
        if self.api_protocol not in ("1.0", "2.0"):
            raise ValueError("Incorrect protocol version")
        if self.api_protocol == "2.0" and self.request_type != "json":
            raise ValueError("In protocol '2.0' only json allowed")

    def _headers(self):
        """
        :return: request headers
        """
        return {
            "User-Agent": self.user_agent,
            "Content-Type": helper.get_request_type(self.request_type),
        }

    def get_signed_data(self, data, headers=None):
        if "merchant_id" not in data:
            data["merchant_id"] = self.merchant_id
        if "reservation_data" in data:
            data["reservation_data"] = utils.to_b64(data["reservation_data"])

        if self.api_protocol == "2.0":
            b64_data = utils.to_b64({"order": data})
            data_v2 = {
                "data": b64_data,
                "version": self.api_protocol,
                "signature": helper.get_signature(
                    self.secret_key, b64_data, self.api_protocol
                ),
            }
            data_string = utils.to_json({"request": data_v2})
        else:
            if "signature" not in data:
                data["signature"] = helper.get_signature(
                    self.secret_key, data, self.api_protocol
                )
            data_string = helper.get_data({"request": data}, self.request_type)

        return (
            data_string,
            utils.merge_dict(headers, self._headers()),
        )

    def post(self, url, data=list, headers=None):
        """
        :param url: endpoint api url
        :param data: request data
        :param headers: request headers
        :return: request
        """
        log.debug("Protocol version: %s" % self.request_type)

        if "merchant_id" not in data:
            data["merchant_id"] = self.merchant_id
        if "reservation_data" in data:
            data["reservation_data"] = utils.to_b64(data["reservation_data"])

        if self.api_protocol == "2.0":
            b64_data = utils.to_b64({"order": data})
            data_v2 = {
                "data": b64_data,
                "version": self.api_protocol,
                "signature": helper.get_signature(
                    self.secret_key, b64_data, self.api_protocol
                ),
            }
            data_string = utils.to_json({"request": data_v2})
        else:
            if "signature" not in data:
                data["signature"] = helper.get_signature(
                    self.secret_key, data, self.api_protocol
                )
            data_string = helper.get_data({"request": data}, self.request_type)

        return self._request(
            utils.join_url(self.api_url, url),
            "POST",
            data=data_string,
            headers=utils.merge_dict(headers, self._headers()),
        )


class Api(BaseAPI):
    is_async = False

    def __init__(self, **kwargs):

        if not requests:
            raise ModuleNotFoundError("Run 'pip install -U requests' to work with Api")
        super().__init__(**kwargs)
