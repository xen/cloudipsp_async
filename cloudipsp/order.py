from __future__ import absolute_import, unicode_literals
from cloudipsp.resources import Resource

import cloudipsp.helpers as helper


class Order(Resource):
    def api_settlement(self, data):
        """
        Method for create split order
        :param data: split order data
        :return: api response
        """
        if self.api.api_protocol != "2.0":
            raise Exception("This method allowed only for v2.0")
        params = {
            "order_type": data.get("order_type", "settlement"),
            "order_id": data.get("order_id") or helper.generate_order_id(),
            "operation_id": data.get("operation_id", ""),
            "receiver": data.get("receiver", []),
        }
        helper.check_data(params)
        params.update(data)
        return "/settlement/", params

    def api_capture(self, data):
        """
        Method for capturing order
        :param data: capture order data
        :return: api response
        """
        params = {
            "order_id": data.get("order_id", ""),
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/capture/order_id/", params

    def api_reverse(self, data):
        """
        Method to reverse order
        :param data: reverse order data
        :return: api response
        """
        params = {
            "order_id": data.get("order_id", ""),
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/reverse/order_id/", params

    def api_status(self, data):
        """
        Method for checking order status
        :param data: order data
        :return: api response
        """
        params = {"order_id": data.get("order_id", "")}
        helper.check_data(params)
        params.update(data)
        return "/status/order_id/", params

    def api_transaction_list(self, data):
        """
        Method for getting order transaction list
        :param data: order data
        :return: api response
        """
        params = {"order_id": data.get("order_id", "")}
        helper.check_data(params)
        params.update(data)
        """
        only json allowed all other methods returns 500 error
        """
        self.api.request_type = "json"
        return "/transaction_list/", params

    def api_atol_logs(self, data):
        """
        Method for getting order atol logs
        :param data: order data
        :return: api response
        """
        params = {"order_id": data.get("order_id", "")}
        helper.check_data(params)
        params.update(data)
        self.api.request_type = "json"
        return "/get_atol_logs/", params
