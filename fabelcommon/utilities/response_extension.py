from requests import Response, HTTPError


class ResponseExtension:
    @staticmethod
    def raise_for_error(response: Response):
        if 400 <= response.status_code < 600:
            raise HTTPError(
                f'Error {response.status_code} calling {response.request.url}, details: {response.text}',
                response=response
            )
