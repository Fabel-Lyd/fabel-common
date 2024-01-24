# file must be in the root to discover tests by pytest run from command line
import json
import pytest
from rest_framework import status


@pytest.fixture
def patch_bokbasen_token(requests_mock):
    return requests_mock.post(
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
