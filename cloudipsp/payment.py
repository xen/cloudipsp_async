from __future__ import absolute_import, unicode_literals
from cloudipsp.resources import Resource
from datetime import datetime

import cloudipsp.helpers as helper


class Pcidss(Resource):
    def api_step_one(self, data):
        """
        Accept purchase Pcidss step one
        :param data: order data
        :return: payment result or step two data
        """
        self.order_id = data.get("order_id") or helper.generate_order_id()
        order_desc = data.get("order_desc") or helper.get_desc(self.order_id)
        params = {
            "order_id": self.order_id,
            "order_desc": order_desc,
            "currency": data.get("currency", ""),
            "amount": data.get("amount", ""),
            "card_number": data.get("card_number", ""),
            "cvv2": data.get("cvv2", ""),
            "expiry_date": data.get("expiry_date", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/3dsecure_step1/", params

    def api_step_two(self, data):
        """
        Accept purchase Pcidss step two
        :param data: order data
        :return: payment result
        """
        params = {
            "order_id": data.get("order_id", ""),
            "pares": data.get("pares", ""),
            "md": data.get("md", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/3dsecure_step2/", params


class Payment(Resource):
    def api_p2pcredit(self, data):
        """
        Method P2P card credit
        :param data: order data
        :return: api response
        """
        self.order_id = data.get("order_id") or helper.generate_order_id()
        order_desc = data.get("order_desc") or helper.get_desc(self.order_id)
        params = {
            "order_id": self.order_id,
            "order_desc": order_desc,
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/p2pcredit/", params

    def api_reports(self, data):
        """
        Method to get payment reports from date range
        :param data: date range
        :return: api response
        """
        params = {
            "date_from": data.get("date_from", ""),
            "date_to": data.get("date_to", ""),
        }
        helper.check_data(params)
        """
        from api only one response if data invalid "General Decline"
        """
        self._validate_reports_date(params)
        params.update(data)
        return "/reports/", params

    def api_recurring(self, data):
        """
        Method for recurring payment
        :param data: order data
        :return: api response
        """
        self.order_id = data.get("order_id") or helper.generate_order_id()
        order_desc = data.get("order_desc") or helper.get_desc(self.order_id)
        params = {
            "order_id": self.order_id,
            "order_desc": order_desc,
            "amount": data.get("amount", ""),
            "currency": data.get("currency", ""),
            "rectoken": data.get("rectoken", ""),
        }
        helper.check_data(params)
        params.update(data)
        return "/recurring/", params

    @staticmethod
    def _validate_reports_date(date):
        """
        Validating date range
        :param date: date
        """
        try:
            date_from = datetime.strptime(date["date_from"], "%d.%m.%Y %H:%M:%S")
            date_to = datetime.strptime(date["date_to"], "%d.%m.%Y %H:%M:%S")
        except ValueError:
            raise ValueError("Incorrect date format.")
        if date_from > date_to:
            raise ValueError("`date_from` can't be greater than `date_to`")
