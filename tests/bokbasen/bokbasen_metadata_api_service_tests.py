import json
from typing import Dict
import pytest
from freezegun import freeze_time
from requests import HTTPError
from rest_framework import status
from fabelcommon.access_token import AccessToken
from fabelcommon.bokbasen.bokbasen_metadata_api_service import BokbasenMetadataApiService


def test_token_request_data() -> None:

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_url="test_url",
        auth_path="test_auth_path"
    )
    result: Dict = bokbasen_metadata_api_service._token_request_data

    assert result['client_id'] == "test_client_id"
    assert result['client_secret'] == "test_client_secret"
    assert result['audience'] == "https://api.bokbasen.io/metadata/"
    assert result['grant_type'] == "client_credentials"


@freeze_time('2012-01-14 12:00:00')
def test_create_authorization_header() -> None:

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_url="test_url",
        auth_path="test_auth_path"
    )

    header = bokbasen_metadata_api_service._create_authorization_header(access_token='test_access_token')
    assert header == {
        'Authorization': 'Bearer test_access_token',
        'Date': 'Sat, 14 Jan 2012 12:00:00 GMT'
    }


def test_create_token(requests_mock) -> None:
    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=status.HTTP_200_OK,
        text=json.dumps({
            "access_token": "fake-access-token",
            "scope": "export:onix",
            "expires_in": 86400,
            "token_type": "Bearer"
        })
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_url="test_url",
        auth_path="https://login.bokbasen.io/oauth/token"
    )

    token: AccessToken = bokbasen_metadata_api_service._get_token_non_cached(
        bokbasen_metadata_api_service._token_request_data
    )
    assert token.access_token_value == "fake-access-token"
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
        requests_mock
) -> None:
    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=expected_status_code,
        text=json.dumps(response_text)
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_url="test_url",
        auth_path="https://login.bokbasen.io/oauth/token"
    )

    with pytest.raises(HTTPError) as exception:

        bokbasen_metadata_api_service._get_token_non_cached(
            bokbasen_metadata_api_service._token_request_data
        )

    assert str(exception.value) == expected_error
