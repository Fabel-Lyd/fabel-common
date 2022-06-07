import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.datetime.time_formats import TimeFormats


def test_send_request_successful(mocker, requests_mock):
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


def test_send_request_failed(mocker, requests_mock):
    mocker.patch.object(BokbasenApiService, attribute='get_ticket', return_value='fake_ticket')

    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_400_BAD_REQUEST
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError):
        bokbasen_service.send_request(HttpVerb.POST, 'https://login.boknett.no/v1/tickets')


def test_get_ticket_successful(requests_mock):

    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_200_OK,
        headers={'boknett-TGT': 'fake-ticket'}
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')
    ticket = bokbasen_service.get_ticket()

    assert ticket == 'fake-ticket'


def test_get_ticket_unsuccessful(requests_mock):
    requests_mock.post(
        'https://login.boknett.no/v1/tickets',
        status_code=status.HTTP_400_BAD_REQUEST,
        headers={'boknett-TGT': 'fake-ticket'}
    )

    bokbasen_service = BokbasenApiService('fake_username', 'fake-password')

    with pytest.raises(HTTPError):
        bokbasen_service.get_ticket()


def test_create_headers(mocker):
    mocker.patch.object(
        TimeFormats,
        attribute='get_date_time',
        return_value='Thu, 02 Jun 2022 08:18:12 GMT')

    headers = BokbasenApiService.create_headers('fake_ticket')

    headers_expected = {
        'Authorization': 'Boknett fake_ticket',
        'Date': 'Thu, 02 Jun 2022 08:18:12 GMT',
        'Accept': 'application/json'
    }

    assert headers == headers_expected
