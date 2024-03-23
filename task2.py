import asyncio
import os
from typing import Optional, Tuple, Union

import aiohttp
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class TickerInfo:
    last: float  # Last price
    baseVolume: float  # Base currency volume_24h
    quoteVolume: float  # Target currency volume_24h


Symbol = str  # Trading pair like ETH/USDT


class BaseExchange:
    async def fetch_data(self, url: str):
        """
        :param url: URL to fetch the data from exchange
        :return: raw data
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp and resp.status == 200:
                    data = await resp.json()
                else:
                    raise Exception(resp)
        return data

    async def fetch_tickers(self) -> dict[Symbol, TickerInfo]:
        """
            Method fetch data from exchange and return all tickers
            in normalized format
            :return:
        """
        raise NotImplementedError

    def normalize_data(self, data: dict) -> dict[Symbol, TickerInfo]:
        """
            :param data: raw data received from the exchange
            :return: normalized data in a common format
        """
        raise NotImplementedError

    def _convert_symbol_to_ccxt(self, symbols: str) -> Symbol:
        """
            Trading pairs from the exchange can come in various
            formats like: btc_usdt, BTCUSDT, etc.
            Here we convert them to a value like: BTC/USDT.
            The format is as follows: separator "/" and all characters
            in uppercase
            :param symbols: Trading pair ex.: BTC_USDT
            :return: BTC/USDT
        """
        raise NotImplementedError

    async def load_markets(self):
        """
            Sometimes the exchange does not have a route
            to receive all the tickers at once.
            In this case, you first need to get a list of all
            trading pairs and save them to self.markets.(Ex.2)
            And then get all these tickers one at a time.
            Allow for delays between requests so as not to exceed the limits
            (you can find the limits in the documentation for
            the exchange API)
        """

    async def close(self):
        pass  # stub, not really needed


class MyExchange(BaseExchange):
    """
        docs: todo Add a link to the API documentation here
    """

    def __init__(self):
        self.id = 'coingecko'
        self.base_url = 'https://api.coingecko.com/api/v3/'
        self.markets = {}

    # Перепишем функцию, добавив паузу и хэдер API-ключа
    async def fetch_data(self, url: str):
        """
        :param url: URL to fetch the data from exchange
        :return: raw data
        """
        headers = {'x-cg-demo-api-key': os.getenv('API_KEY', '')}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                if resp and resp.status == 200:
                    data = await resp.json()
                else:
                    raise Exception(resp)
        await asyncio.sleep(2)
        return data

    def _convert_symbol_to_ccxt(self, symbols: str) -> Symbol:
        pass

    def _find_identical_coins(
        self,
        base_currencies_list: list,
        currency: str,
    ) -> list:

        identical_symbols_coins = filter(
            lambda x: x['symbol'] == currency,
            base_currencies_list,
        )
        return list(identical_symbols_coins)

    def _convert_trading_pair_name(self, base: str, target: str) -> str:
        return f"{base.upper()}/{target.upper()}"

    def _process_trading_pair_vs_currency(
        self,
        trading_pair: dict,
        vs_currency: str,
    ) -> Union[Tuple[None, None], Tuple[str, dict]]:

        # Обрабатываем только те случаи, где валюты не совпадают
        if trading_pair['symbol'] != vs_currency:

            # Поскольку данные с сервиса приходят разобщенные, приходится
            # склеивать название из разных источников,
            # приходится склеивать название пары из разных источников
            # (станд. реализация через одну переменную не сработает)
            trading_pair_name = self._convert_trading_pair_name(
                trading_pair['symbol'],
                vs_currency,
            )

            # Создаем базовый словарь для хранения данных
            info = {
                'last': trading_pair['current_price'],
                'baseVolume': 0.0,
                'quoteVolume': trading_pair['total_volume'],
            }

            return trading_pair_name, info

        return None, None

    def _check_base_value_for_volume(
        self,
        base_currency: str,
        vs_currency: str,
        base_currencies_list: list,
        vs_currencies_list: list,
    ) -> Optional[str]:

        # Проверяем наличие vs_currency в списке базовых валют и
        # находим истинную.
        # В исходном списке присутствует много лишней информации.
        # По наблюдениям истинной валютой
        # является валюта с самым коротким id
        identical_symbols_coins = self._find_identical_coins(
            base_currencies_list,
            vs_currency,
        )

        if (identical_symbols_coins != []) and (base_currency in vs_currencies_list):  # noqa: E501
            identical_symbols_ids = [
                el['id'] for el in identical_symbols_coins
            ]
            true_id = min(identical_symbols_ids)
            return true_id

        return None

    async def _get_base_volume(
        self,
        vs_currency_based_id: str,
        base_id: str,
    ) -> int:

        # Создаем обратный запрос, чтобы пересчитать baseVolume
        # в рамках trading pair
        subresponse = await self.fetch_data(
            f"{self.base_url}/coins/markets/?ids={vs_currency_based_id}&vs_currency={base_id}")  # noqa: E501

        return subresponse[0]['total_volume']

    def normalize_data(self, data: dict) -> dict[Symbol, TickerInfo]:

        normalized_data = {}

        for key, val in data.items():
            normalized_data[key] = TickerInfo(
                last=val['last'],
                baseVolume=val['baseVolume'],
                quoteVolume=val['quoteVolume'],
            )

        return normalized_data

    async def fetch_tickers(self) -> dict[Symbol, TickerInfo]:

        # Получаем базовый список валют и vs_currencies.
        # Изначально смутила формулировка total_volume. 
        # Планировал уже пересчитывать через объемы продаж по часам,
        # так как если задать на эндпоинте посуточную информацию, 
        # начинает считать от полуночаи, а не сутки назад от текущего времени.
        # Более того, выяснил, что даже почасовая информация дается не в абсо-
        # лютных величинах, а скользящие значения посуточных величин от
        # конкретного часа. Так что остановился на варианте ниже,
        # тем более что по сверке с сайтом информация около-актуальная.
        base_currencies = await self.fetch_data(f"{self.base_url}/coins/list")
        vs_currencies = await self.fetch_data(f"{self.base_url}/simple/supported_vs_currencies")  # noqa: E501

        data = {}

        for vs_currency in vs_currencies:

            # По каждой vs_currency просматриваем курсы
            # относительно базовых валют
            response = await self.fetch_data(f"{self.base_url}/coins/markets/?vs_currency={vs_currency}&category=cryptocurrency")  # noqa: E501

            for trading_pair in response:

                # Обрабатываем основной запрос: проверяем,
                # чтобы базовая и котируемая валюты
                # не дублировались, конвертируем имя,
                # создаем словарь с информацией
                key, val = self._process_trading_pair_vs_currency(
                    trading_pair,
                    vs_currency,
                )

                # Если ключа нет (валюты дублируются) - пропускаем остальное
                if key is None:
                    continue

                # Проверяем, есть ли vs_currency в общем списке,
                # и есть ли базовая валюта в списке vs_currencies
                # для возможности расчет baseVolume через обратный запрос.
                # Вернется либо нужный id, либо None
                id_for_base_volume = self._check_base_value_for_volume(
                    trading_pair['symbol'],
                    vs_currency,
                    base_currencies,
                    vs_currencies,
                )

                # Переписываем baseVolume
                if id_for_base_volume:
                    val['baseVolume'] = await self._get_base_volume(
                        id_for_base_volume,
                        trading_pair['symbol'],
                    )

                # Создаем пару ключ-значение в словаре и
                # тут же просматриваем в консоли
                data[key] = val
                print(f'data: {key}')
                print(f'value: {val}')

        return self.normalize_data(data)

    async def load_markets(self):
        pass


async def main():
    """
        Test yourself here.
        Verify prices and volumes here: https://www.coingecko.com/
    """
    exchange = MyExchange()
    await exchange.load_markets()
    tickers = await exchange.fetch_tickers()
    for symbol, prop in tickers.items():
        print(symbol, prop)

    assert isinstance(tickers, dict)
    for symbol, prop in tickers.items():
        assert isinstance(prop, TickerInfo)
        assert isinstance(symbol, Symbol)

if __name__ == "__main__":
    asyncio.run(main())
