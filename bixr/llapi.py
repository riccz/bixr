import datetime
import typing as ty

from urllib.parse import urljoin
from pathlib import Path

from requests_cache import CachedSession


BASE_URL = "https://tassidicambio.bancaditalia.it/terzevalute-wf-web/rest/v1.0/"
DEFAULT_CACHE = Path("~/.cache/bixr").expanduser()
DEFAULT_EXPIRE = 3600 * 24 * 7
EXPIRE_OVERRIDES = {
    "**/latest": 60,
    "**/daily": 3600 * 24,
    # "**/monthly": 3600 * 24 * 30,
    # "**annual": 3600 * 24 * 365,
}

# All dates are in CET/CEST
# Data is only available for (Italian) workdays
# Rates can be Base/quote (C) or quote/base (I) see `exchangeConventionCode`
# Ranges include both extremes


class LLAPI:
    def __init__(self, lang="en"):
        self.lang = lang
        self.session = CachedSession(
            DEFAULT_CACHE,
            expire_after=DEFAULT_EXPIRE,
            urls_expire_after=EXPIRE_OVERRIDES,
        )
        self.session.headers["Accept"] = "application/json"

    def _request(self, method: str, params: ty.Dict[str, str]):
        params.setdefault("lang", self.lang)
        url = urljoin(BASE_URL, method)
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        resp_json = resp.json()
        # resp_json always has `resultsInfo` and another key with the data
        if "totalRecords" in resp_json["resultsInfo"]:
            (other_key,) = filter(lambda k: k != "resultsInfo", resp_json.keys())
            assert len(resp_json[other_key]) == resp_json["resultsInfo"]["totalRecords"]
        return resp_json

    def _request_with_lang(
        self,
        method: str,
        lang: ty.Optional[str],
        params: ty.Dict[str, str],
    ):
        params = params.copy()
        assert "lang" not in params
        if lang:
            params["lang"] = lang
        return self._request(method, params)

    def latest(self, lang: ty.Optional[str] = None):
        return self._request_with_lang("latestRates", lang, {})

    def currencies(self, lang: ty.Optional[str] = None):
        return self._request_with_lang("currencies", lang, {})

    def daily(
        self,
        date: datetime.date,
        quote_currency: str,
        base_currency: ty.Optional[ty.Union[str, ty.Iterable[str]]] = None,
        lang: ty.Optional[str] = None,
    ):
        params = {"referenceDate": date.isoformat(), "currencyIsoCode": quote_currency}
        if isinstance(base_currency, str):
            params["baseCurrencyIsoCode"] = base_currency
        elif base_currency:
            params["baseCurrencyIsoCode"] = list(base_currency)

        return self._request_with_lang("dailyRates", lang, params)

    def monthly(
        self,
        year: int,
        month: int,
        quote_currency: str,
        base_currency: ty.Optional[ty.Union[str, ty.Iterable[str]]] = None,
        lang: ty.Optional[str] = None,
    ):
        params = {
            "year": str(year),
            "month": str(month),
            "currencyIsoCode": quote_currency,
        }
        if isinstance(base_currency, str):
            params["baseCurrencyIsoCode"] = base_currency
        elif base_currency:
            params["baseCurrencyIsoCode"] = list(base_currency)

        return self._request_with_lang("monthlyAverageRates", lang, params)

    def yearly(
        self,
        year: int,
        quote_currency: str,
        base_currency: ty.Optional[ty.Union[str, ty.Iterable[str]]] = None,
        lang: ty.Optional[str] = None,
    ):
        params = {"year": str(year), "currencyIsoCode": quote_currency}
        if isinstance(base_currency, str):
            params["baseCurrencyIsoCode"] = base_currency
        elif base_currency:
            params["baseCurrencyIsoCode"] = list(base_currency)

        return self._request_with_lang("annualAverageRates", lang, params)

    def daily_range(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        base_currency: str,
        quote_currency: str,
        lang: ty.Optional[str] = None,
    ):
        return self._request_with_lang(
            "dailyTimeSeries",
            lang,
            {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "baseCurrencyIsoCode": base_currency,
                "currencyIsoCode": quote_currency,
            },
        )

    def monthly_range(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        base_currency: str,
        quote_currency: str,
        lang: ty.Optional[str] = None,
    ):
        return self._request_with_lang(
            "monthlyTimeSeries",
            lang,
            {
                "startYear": str(start_year),
                "startMonth": str(start_month),
                "endYear": str(end_year),
                "endMonth": str(end_month),
                "baseCurrencyIsoCode": base_currency,
                "currencyIsoCode": quote_currency,
            },
        )

    def yearly_range(
        self,
        start_year: int,
        end_year: int,
        base_currency: str,
        quote_currency: str,
        lang: ty.Optional[str] = None,
    ):
        return self._request_with_lang(
            "annualTimeSeries",
            lang,
            {
                "startYear": str(start_year),
                "endYear": str(end_year),
                "baseCurrencyIsoCode": base_currency,
                "currencyIsoCode": quote_currency,
            },
        )
