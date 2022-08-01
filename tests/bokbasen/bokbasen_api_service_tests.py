import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export_response import BokbasenExportResponse


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
        status_code=status.HTTP_400_BAD_REQUEST
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError):
        bokbasen_service.send_request(HttpVerb.POST, 'https://login.boknett.no/v1/tickets')


def test_send_export_request(mocker, requests_mock):
    mocker.patch.object(BokbasenApiService, attribute='get_ticket', return_value='fake_ticket')
    requests_mock.get(
        'https://api.boknett.no/export',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text='exported_text'
    )

    expected_response: BokbasenExportResponse = BokbasenExportResponse('exported_text', 'cursor')

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')
    actual_response: BokbasenExportResponse = bokbasen_service.send_export_request('https://api.boknett.no/export')

    assert actual_response == expected_response


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
        'Date': 'Thu, 02 Jun 2022 08:18:12 GMT',
    }

    assert headers == headers_expected
