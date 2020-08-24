import asyncio
from cloudipsp import AsyncAPI, Checkout


async def main():
    api = AsyncAPI(
        merchant_id=1396424,
        secret_key="test",
        request_type="json",
        api_protocol="1.0",
        api_domain="api.fondy.eu",
    )  # json - is default
    checkout = Checkout(api=api)
    data = {
        "preauth": "Y",
        "currency": "RUB",
        "amount": 10000,
        "reservation_data": {"test": 1, "test2": 2},
    }
    response = await checkout.url(data)
    print(response)


asyncio.get_event_loop().run_until_complete(main())
