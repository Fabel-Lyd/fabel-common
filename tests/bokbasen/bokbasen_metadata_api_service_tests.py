import json
from typing import Dict
import pytest
from freezegun import freeze_time
from requests import HTTPError
from rest_framework import status
from fabelcommon.access_token import AccessToken
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.export_response import BokbasenExportResponse
from fabelcommon.http.verbs import HttpVerb


def test_token_request_data(mock_bokbasen_metadata_api_service) -> None:
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)
    result: Dict = bokbasen_metadata_api_service._token_request_data
    assert result['client_id'] == 'test_client_id'
    assert result['client_secret'] == 'test_client_secret'
    assert result['audience'] == 'https://api.bokbasen.io/metadata/'
    assert result['grant_type'] == 'client_credentials'


@freeze_time('2012-01-14 12:00:00')
def test_create_authorization_header(mock_bokbasen_metadata_api_service) -> None:
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)
    header: Dict = bokbasen_metadata_api_service._create_authorization_header(access_token='test_access_token')
    assert header == {
        'Authorization': 'Bearer test_access_token',
        'Date': 'Sat, 14 Jan 2012 12:00:00 GMT'
    }


def test_get_token_success(
        patch_bokbasen_token,
        mock_bokbasen_metadata_api_service
) -> None:
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)
    token: AccessToken = bokbasen_metadata_api_service._get_token()
    assert token.access_token_value == 'fake-access-token'
    assert token.is_valid is True
    assert token.user_id is None


@pytest.mark.parametrize(
    'expected_status_code, response_text, expected_error',
    [
        (
            status.HTTP_401_UNAUTHORIZED,
            {
                "error": "access_denied",
                "error_description": "Unauthorized"
            },
            'Error 401 calling https://login.bokbasen.io/oauth/token'
            ', details: {"error": "access_denied", "error_description": "Unauthorized"}'
        ),
        (
            status.HTTP_403_FORBIDDEN,
            {
                "error": "access_denied",
                "error_description": "Service not enabled within domain: https://api.bokbasen.io/metadatax/"
            },
            'Error 403 calling https://login.bokbasen.io/oauth/token'
            ', details: {"error": "access_denied",'
            ' "error_description": "Service not enabled within domain: https://api.bokbasen.io/metadatax/"}'
        )
    ]
)
def test_create_access_token_invalid(
        expected_status_code,
        response_text,
        expected_error,
        requests_mock,
        mock_bokbasen_metadata_api_service
) -> None:
    requests_mock.post(
        url='https://login.bokbasen.io/oauth/token',
        status_code=expected_status_code,
        text=json.dumps(response_text)
    )
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)
    with pytest.raises(HTTPError) as exception:
        bokbasen_metadata_api_service._get_token()

    assert str(exception.value) == expected_error


def test_send_request_with_token_expired(
        requests_mock,
        mock_bokbasen_metadata_api_service
) -> None:
    access_token_call = requests_mock.post(
        url='https://login.bokbasen.io/oauth/token',
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                'access_token': 'fake-access-token',
                'scope': 'export:onix',
                'expires_in': 86400,
                'token_type': 'Bearer'
            }
        )
    )

    requests_mock.get(
        url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533',
        status_code=status.HTTP_200_OK,
        text='fake_response_data'
    )

    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)
    with freeze_time('2012-01-14 12:00:00'):
        bokbasen_metadata_api_service.send_request(
            verb=HttpVerb.GET,
            url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533')

    with freeze_time('2012-01-15 12:00:00'):
        response: str = bokbasen_metadata_api_service.send_request(
            verb=HttpVerb.GET,
            url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533')

    assert access_token_call.call_count == 2
    assert response == 'fake_response_data'


def test_send_request_token_not_expired(
        requests_mock,
        mock_bokbasen_metadata_api_service
) -> None:
    get_new_access_token = requests_mock.post(
        url='https://login.bokbasen.io/oauth/token',
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                'access_token': 'fake-access-token',
                'scope': 'export:onix',
                'expires_in': 86400,
                'token_type': 'Bearer'
            }
        )
    )

    requests_mock.get(
        url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533',
        status_code=status.HTTP_200_OK,
        text='some_test_data'
    )
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)

    with freeze_time('2012-01-14 12:00:00'):
        bokbasen_metadata_api_service.send_request(
            verb=HttpVerb.GET,
            url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533')

    with freeze_time('2012-01-14 15:00:00'):
        response: str = bokbasen_metadata_api_service.send_request(
            verb=HttpVerb.GET,
            url='https://api.bokbasen.io/metadata/export/onix/v1/9788248933533')
    assert get_new_access_token.call_count == 1
    assert response == 'some_test_data'


def test_send_export_request(
        requests_mock,
        patch_bokbasen_token,
        mock_bokbasen_metadata_api_service
):

    requests_mock.get(
        url='https://api.bokbasen.io/metadata/export/onix/v1',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text='exported_text'
    )

    expected_response: BokbasenExportResponse = BokbasenExportResponse('exported_text', 'cursor')
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)

    actual_response: BokbasenExportResponse = bokbasen_metadata_api_service.send_export_request('https://api.bokbasen.io/metadata/export/onix/v1')

    assert actual_response == expected_response


def test_send_order_request(
        patch_bokbasen_token,
        mock_bokbasen_metadata_api_service,
        requests_mock
) -> None:

    requests_mock.post(
        url='https://api.dds.boknett.no/order',
        headers={'Location': 'https://api.dds.boknett.no/content/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'},
        status_code=status.HTTP_201_CREATED
    )
    bokbasen_metadata_api_service = mock_bokbasen_metadata_api_service(BokbasenAudience.METADATA)

    response = bokbasen_metadata_api_service.send_order_request(
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
