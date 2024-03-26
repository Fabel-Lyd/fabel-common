# file must be in the root to discover tests by pytest run from command line
import json
import pytest
from rest_framework import status
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService


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
def mock_bokbasen_api_service():
    def _factory(bokbasen_audience: BokbasenAudience):
        bokbasen_api_service: BokbasenApiService = BokbasenApiService(
            client_id='test_client_id',
            client_secret='test_client_secret',
            base_url='https://api.bokbasen.io',
            auth_path='https://auth.bokbasen.io/oauth/token',
            audience=bokbasen_audience
        )
        return bokbasen_api_service
    return _factory
