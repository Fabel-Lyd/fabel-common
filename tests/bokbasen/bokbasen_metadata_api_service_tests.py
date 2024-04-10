from typing import Dict
from rest_framework import status
from fabelcommon.bokbasen.export_response import BokbasenExportResponse


def test_token_request_data(mock_bokbasen_metadata_api_service) -> None:
    result: Dict = mock_bokbasen_metadata_api_service._token_request_data
    assert result['client_id'] == 'test_client_id'
    assert result['client_secret'] == 'test_client_secret'
    assert result['audience'] == 'https://api.bokbasen.io/metadata/'
    assert result['grant_type'] == 'client_credentials'


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
    actual_response: BokbasenExportResponse = mock_bokbasen_metadata_api_service.send_export_request('https://api.bokbasen.io/metadata/export/onix/v1')

    assert actual_response == expected_response
