from abc import ABC
from typing import Dict, Any
import requests
from requests import Response
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.bokbasen.export_response import BokbasenExportResponse


class BokbasenApiService(ABC):
    BASE_URL: str = 'https://api.boknett.no'

    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password

    @staticmethod
    def create_headers(ticket: str) -> Dict[str, str]:

        headers: Dict[str, str] = {
            "Authorization": f"Boknett {ticket}",
            "Date": TimeFormats.get_date_time(),
        }
        return headers

    def get_ticket(self) -> str:

        url: str = 'https://login.boknett.no/v1/tickets'

        params: Dict[str, str] = {
            "username": self._username,
            "password": self._password
        }

        response: Response = requests.post(url, params)
        response.raise_for_status()

        return response.headers['boknett-TGT']

    def send_request(self, verb: HttpVerb, url: str, data: Any = None) -> str:
        response: Response = self.__send_request(verb, url, data)
        return response.text

    def send_export_request(self, url: str) -> BokbasenExportResponse:
        response: Response = self.__send_request(HttpVerb.GET, url, None)
        return BokbasenExportResponse(content=response.text, cursor=response.headers['next'])

    def __send_request(self, verb: HttpVerb, url: str, data: Any) -> Response:
        token: str = self.get_ticket()
        headers: Dict[str, str] = self.create_headers(token)

        response: Response = requests.request(verb.value, url, headers=headers, data=data)
        response.raise_for_status()

        return response
