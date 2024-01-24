import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.bokbasen.export_response.download_response import DownloadResponse
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService


def test_send_request_successful(mocker, requests_mock) -> None:
    mocker.patch.object(BokbasenApiService, attribute='get_ticket', return_value='fake_ticket')

    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        headers={'boknett-TGT': 'fake-ticket'},
        status_code=status.HTTP_200_OK,
        text='fake-ticket'
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')
    response = bokbasen_service.send_request(HttpVerb.POST, 'https://login.boknett.no/v1/tickets')

    assert response == 'fake-ticket'


def test_send_request_failed(mocker, requests_mock) -> None:
    mocker.patch.object(BokbasenApiService, attribute='get_ticket', return_value='fake_ticket')

    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_400_BAD_REQUEST,
        text='Http error message'
    )

    bokbasen_service: BokbasenApiService = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError) as http_error:
        bokbasen_service.send_request(HttpVerb.POST, 'https://login.boknett.no/v1/tickets')

    assert str(http_error.value) == 'Error 400 calling https://login.boknett.no/v1/tickets, details: Http error message'


def test_send_order_request(mocker, requests_mock) -> None:
    mocker.patch.object(
        target=BokbasenApiService,
        attribute='get_ticket',
        return_value='fake_ticket'
    )

    requests_mock.post(
        url='https://api.dds.boknett.no/order',
        headers={'Location': 'https://api.dds.boknett.no/content/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'},
        status_code=status.HTTP_201_CREATED
    )

    bokbasen_api_service = BokbasenApiService('fake_username', 'fake-password')
    response = bokbasen_api_service.send_order_request(
        verb=HttpVerb.POST,
        url='https://api.dds.boknett.no/order',
        data={"order_id": "222092-1-1",
              "isbn": "1234567890",
              "price": "26200",
              "firstname": "John",
              "lastname": "Smith",
              "email": "john.smith@fabel.no"}
    )
    assert response.location == 'https://api.dds.boknett.no/content/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'


def test_send_order_request_unsuccessful(mocker, requests_mock):
    mocker.patch.object(
        target=BokbasenApiService,
        attribute='get_ticket',
        return_value='fake_ticket'
    )

    requests_mock.post(
        url='https://api.dds.boknett.no/order',
        headers={'Location': 'https://api.dds.boknett.no/content/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'},
        status_code=status.HTTP_400_BAD_REQUEST
    )

    bokbasen_api_service = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError):
        bokbasen_api_service.send_order_request(
            verb=HttpVerb.POST,
            url='https://api.dds.boknett.no/order',
            data={"order_id": "222092-1-1",
                  "isbn": "1234567890",
                  "price": "26200",
                  "firstname": "John",
                  "lastname": "Smith",
                  "email": "john.smith@fabel.no"}
        )


def test_get_ticket_successful(requests_mock) -> None:
    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_200_OK,
        headers={'boknett-TGT': 'fake-ticket'}
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')
    ticket = bokbasen_service.get_ticket()

    assert ticket == 'fake-ticket'


def test_get_ticket_unsuccessful(requests_mock) -> None:
    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_400_BAD_REQUEST,
        headers={'boknett-TGT': 'fake-ticket'}
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError):
        bokbasen_service.get_ticket()


def test_create_headers(mocker) -> None:
    mocker.patch.object(
        TimeFormats,
        attribute='get_date_time',
        return_value='Thu, 02 Jun 2022 08:18:12 GMT')

    headers = BokbasenApiService.create_headers('fake_ticket')

    headers_expected = {
        'Authorization': 'Boknett fake_ticket',
        'Date': 'Thu, 02 Jun 2022 08:18:12 GMT'
    }

    assert headers == headers_expected


def test_send_download_url_request(requests_mock, mocker):
    mocker.patch.object(
        BokbasenApiService,
        attribute='get_ticket',
        return_value='fake_ticket')

    requests_mock.get(
        'https://api.dds.boknett.no/content/c4029e6e-a237-4c20-a109-804d398122ab?type=audio%2Fvnd.bokbasen.complete-public&bitrate=64',
        headers={'Location': 'https://api.dds.boknett.no/download/adf39c11-a7dc-42b0-b6a2-0313937fb914/status'},
        status_code=status.HTTP_302_FOUND,
    )

    expected_response = DownloadResponse(location='https://api.dds.boknett.no/download/adf39c11-a7dc-42b0-b6a2-0313937fb914/status')

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')
    response = bokbasen_service.send_download_url_request('https://api.dds.boknett.no/content/c4029e6e-a237-4c20-a109-804d398122ab')

    assert response.location == expected_response.location
