from typing import Dict


def test_token_request_data(mock_bokbasen_bokskya_api_service) -> None:
    result: Dict = mock_bokbasen_bokskya_api_service._token_request_data
    assert result['client_id'] == 'test_client_id'
    assert result['client_secret'] == 'test_client_secret'
    assert result['audience'] == 'https://api.bokbasen.io/bokskya/'
    assert result['grant_type'] == 'client_credentials'
