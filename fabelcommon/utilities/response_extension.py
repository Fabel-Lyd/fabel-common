from typing import Dict
from requests import Response, HTTPError


class ResponseExtension:
    @staticmethod
    def raise_for_error(
            response: Response,
            additional_info_mapping: Dict[int, str] = {}
    ):
        if 400 <= response.status_code < 600:
            error_message: str = f'Error {response.status_code} calling {response.request.url}, details: {response.text}'

            if additional_info_mapping.get(response.status_code) is not None:
                error_message = error_message + f', additional info: {additional_info_mapping.get(response.status_code)}'

            raise HTTPError(
                error_message,
                response=response
            )
