from typing import Dict
from rest_framework import status
from fabelcommon.bokbasen.bokbasen_dds_api_service import BokbasenDdsApiService
from fabelcommon.bokbasen.export_response.download_response import DownloadResponse
from fabelcommon.http.verbs import HttpVerb


def test_token_request_data(mock_bokbasen_dds_api_service) -> None:
    result: Dict = mock_bokbasen_dds_api_service._token_request_data
    assert result['client_id'] == 'test_client_id'
    assert result['client_secret'] == 'test_client_secret'
    assert result['audience'] == 'https://api.bokbasen.io/dds/'
    assert result['grant_type'] == 'client_credentials'


def test_send_download_url_request(
        patch_bokbasen_token,
        mock_bokbasen_dds_api_service,
        requests_mock
) -> None:

    requests_mock.get(
        'https://api.bokbasen.io/dds/content/v1/c4029e6e-a237-4c20-a109-804d398122ab?type=audio%2Fvnd.bokbasen.complete-public&bitrate=64',
        headers={'Location': 'https://api.dds.boknett.no/download/adf39c11-a7dc-42b0-b6a2-0313937fb914/status'},
        status_code=status.HTTP_302_FOUND,
    )
    expected_response = DownloadResponse(
        location='https://api.dds.boknett.no/download/adf39c11-a7dc-42b0-b6a2-0313937fb914/status')

    bokbasen_api_service: BokbasenDdsApiService = mock_bokbasen_dds_api_service

    response: DownloadResponse = bokbasen_api_service.send_download_url_request('https://api.bokbasen.io/dds/content/v1/c4029e6e-a237-4c20-a109-804d398122ab')
    assert response.location == expected_response.location


def test_send_order_request(
        patch_bokbasen_token,
        mock_bokbasen_dds_api_service,
        requests_mock
) -> None:

    requests_mock.post(
        url='https://api.bokbasen.io/dds/order/v1',
        headers={'Location': 'https://api.bokbasen.io/dds/content/v1/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'},
        status_code=status.HTTP_201_CREATED
    )
    bokbasen_api_service: BokbasenDdsApiService = mock_bokbasen_dds_api_service

    response = bokbasen_api_service.send_order_request(
        verb=HttpVerb.POST,
        url='https://api.bokbasen.io/dds/order/v1',
        data={"order_id": "222092-1-1",
              "isbn": "1234567890",
              "price": "26200",
              "firstname": "John",
              "lastname": "Smith",
              "email": "john.smith@fabel.no"}
    )
    assert response.location == 'https://api.bokbasen.io/dds/content/v1/0b1c4e50-bb00-46ea-bc24-27d1b32fb2a3'
