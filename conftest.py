# file must be in the root to discover tests by pytest run from command line
import json
import pytest
from rest_framework import status
from fabelcommon.bokbasen.bokbasen_bokskya_api_service import BokbasenBokskyaApiService
from fabelcommon.bokbasen.bokbasen_dds_api_service import BokbasenDdsApiService
from fabelcommon.bokbasen.bokbasen_metadata_api_service import BokbasenMetadataApiService


@pytest.fixture
def patch_bokbasen_token(requests_mock):
    return requests_mock.post(
        url='https://auth.bokbasen.io/oauth/token',
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


@pytest.fixture
def mock_bokbasen_metadata_api_service():
    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService(
        client_id='test_client_id',
        client_secret='test_client_secret',
        base_url='https://api.bokbasen.io',
        auth_path='https://auth.bokbasen.io/oauth/token',
    )
    return bokbasen_metadata_api_service


@pytest.fixture
def mock_bokbasen_dds_api_service():
    bokbasen_dds_api_service: BokbasenDdsApiService = BokbasenDdsApiService(
        client_id='test_client_id',
        client_secret='test_client_secret',
        base_url='https://api.bokbasen.io',
        auth_path='https://auth.bokbasen.io/oauth/token',
    )
    return bokbasen_dds_api_service


@pytest.fixture
def mock_bokbasen_bokskya_api_service():
    bokbasen_bokskya_api_service: BokbasenBokskyaApiService = BokbasenBokskyaApiService(
        client_id='test_client_id',
        client_secret='test_client_secret',
        base_url='https://api.bokbasen.io',
        auth_path='https://auth.bokbasen.io/oauth/token',
    )
    return bokbasen_bokskya_api_service
