from __future__ import absolute_import, unicode_literals
from cloudipsp.resources import Resource
from datetime import datetime

import cloudipsp.helpers as helper


class Checkout(Resource):
    def api_url(self, data):
        """
        Method to generate checkout url
        :param data: order data
        """
        return "/checkout/url/", self._required(data)

    def api_token(self, data):
        """
        Method to generate checkout token
        :param data: order data
        """
        return "/checkout/token/", self._required(data)

    def api_verification(self, data):
        """
        Method to generate checkout verification url
        :param data: order data
        """
        verification_data = {
            "verification": "Y",
            "verification_type": data.get("verification_type", "code"),
        }
        data.update(verification_data)
        return "/checkout/url/", self._required(data)

    def api_subscription(self, data):
        """
        Method to generate checkout url with calendar
        :param data: order data
        data = {
            "currency": "UAH", -> currency ('UAH', 'RUB', 'USD')
            "amount": 10000, -> amount of the order (int)
            "recurring_data": {
                "every": 1, -> frequency of the recurring order (int)
                "amount": 10000, -> amount of the recurring order (int)
                "period": 'month', -> period of the recurring order ('day', 'month', 'year')
                "start_time": '2020-07-24', -> start date of the recurring order ('YYYY-MM-DD')
                "readonly": 'y', -> possibility to change parameters of the recurring order by user ('y', 'n')
                "state": 'y' -> default state of the recurring order after opening url of the order ('y', 'n')
            }
        }
        """
        if self.api.api_protocol != "2.0":
            raise Exception("This method allowed only for v2.0")
        recurring_data = data.get("recurring_data", "")
        subscription_data = {
            "subscription": "Y",
            "recurring_data": {
                "start_time": recurring_data.get("start_time", ""),
                "amount": recurring_data.get("amount", ""),
                "every": recurring_data.get("every", ""),
                "period": recurring_data.get("period", ""),
                "readonly": recurring_data.get("readonly", ""),
                "state": recurring_data.get("state", ""),
            },
        }

        helper.check_data(subscription_data["recurring_data"])
        self._validate_recurring_data(subscription_data["recurring_data"])
        subscription_data.update(data)
        return "/checkout/url/", self._required(subscription_data)

    @staticmethod
    def _validate_recurring_data(data):
        """
        Validation recurring data params
        :param data: recurring data
        :return: exception
        """
        try:
            datetime.strptime(data["start_time"], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect date format. 'Y-m-d' is allowed")
        if data["period"] not in ("day", "week", "month"):
            raise ValueError("Incorrect period. ('day','week','month') is allowed")

    def _required(self, data):
        """
        Required data to send
        :param data:
        :return: parameters to send
        """
        self.order_id = data.get("order_id", helper.generate_order_id())
        order_desc = data.get("order_desc", f"Pay for order #: {self.order_id}")
        params = {
            "order_id": self.order_id,
            "order_desc": order_desc,
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
        }
        helper.check_data(params)
        params.update(data)

        return params
