from abc import ABC
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import requests
from requests import Response
from fabelcommon.bokbasen.export_response.download_response import DownloadResponse
from fabelcommon.bokbasen.export_response.order_response import OrderResponse
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.bokbasen.export_response import BokbasenExportResponse
from fabelcommon.utilities.response_extension import ResponseExtension


class BokbasenApiService(ABC):

    def __init__(
            self,
            username: str,
            password: str,
            base_url: str = 'https://api.boknett.no',
            auth_url: str = 'https://login.boknett.no/v1/tickets'
    ) -> None:

        self._username: str = username
        self._password: str = password
        self._base_url: str = base_url
        self._auth_url: str = auth_url

    @staticmethod
    def create_headers(ticket: str) -> Dict[str, str]:

        headers: Dict[str, str] = {
            "Authorization": f"Boknett {ticket}",
            "Date": TimeFormats.get_date_time()
        }
        return headers

    def get_ticket(self) -> str:

        params: Dict[str, str] = {
            "username": self._username,
            "password": self._password
        }

        response: Response = requests.post(self._auth_url, params)
        response.raise_for_status()

        return response.headers['boknett-TGT']

    def send_request(self, verb: HttpVerb, url: str, data: Any = None, headers_to_add: Optional[Dict[str, str]] = None) -> str:
        response: Response = self.__send_request(
            verb=verb,
            url=url,
            data=data,
            headers_to_add=headers_to_add
        )

        return response.text

    def send_order_request(self, verb: HttpVerb, url: str, data: Any = None) -> OrderResponse:
        response: Response = self.__send_request(
            verb=verb,
            url=url,
            data=data,
            headers_to_add={
                "Accept": "application/json",
                "Content-type": "application/json"
            }
        )
        return OrderResponse(location=response.headers['Location'])

    def send_download_url_request(self, url: str) -> DownloadResponse:

        params: Dict[str, str] = {
            "type": "audio/vnd.bokbasen.complete-public",
            "bitrate": "64"
        }

        response: Response = self.__send_request(
            verb=HttpVerb.GET,
            url=url,
            data=None,
            params=params,
            headers_to_add={"Accept": "application/json"},
            allow_redirect=False
        )

        return DownloadResponse(response.headers['Location'])

    def send_export_request(self, url: str) -> BokbasenExportResponse:
        response: Response = self.__send_request(HttpVerb.GET, url, None)
        return BokbasenExportResponse(content=response.text, cursor=response.headers['next'])

    def __send_request(
            self,
            verb: HttpVerb,
            url: str,
            data: Any,
            params: Optional[Dict] = None,
            headers_to_add: Optional[Dict[str, str]] = None,
            allow_redirect: bool = True
    ) -> Response:
        token: str = self.get_ticket()
        headers: Dict[str, str] = self.create_headers(token)

        if headers_to_add is not None:
            headers.update(headers_to_add)

        response: Response = requests.request(
            method=verb.value,
            url=urljoin(self._base_url, url),
            headers=headers,
            data=data,
            params=params,
            allow_redirects=allow_redirect
        )
        ResponseExtension.raise_for_error(response)

        return response
