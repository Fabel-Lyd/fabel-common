import json
from typing import Dict
from urllib import parse
from fabelcommon.access_token import AccessToken
from fabelcommon.beat.beat_api_service import BeatApiService
from fabelcommon.http.verbs import HttpVerb

token_responses: Dict = {
    'password': {
        'access_token': 'user_token',
        'expires_in': 600,
        'user_id': 117},
    'client_credentials': {
        'access_token': 'credential_token',
        'expires_in': 600}
}


def create_token_response(request, _):
    # noinspection PyProtectedMember
    body = parse.parse_qs(request._request.body)
    grant_type = body['grant_type'][0]
    return json.dumps(token_responses[grant_type])


def test_password_token_should_not_be_cached(requests_mock):

    requests_mock.post('http://localhost/v2/oauth2/token', text=create_token_response)

    beat_api_service: BeatApiService = BeatApiService(
        client_id='client_id',
        client_secret='client_secret',
        base_url='http://localhost/'
    )

    # first `grant_type` `client_credential` call using token caching
    requests_mock.get('http://localhost/credential-protected-endpoint')
    beat_api_service.send_request(
        verb=HttpVerb.GET,
        url='http://localhost/credential-protected-endpoint'
    )

    # `grant_type` `password` call performed
    access_token: AccessToken = beat_api_service.get_password_flow_token('user', 'password')
    requests_mock.get('http://localhost/resource-owner-protected-endpoint')
    beat_api_service.send_request_with_token(
        verb=HttpVerb.GET,
        url='http://localhost/resource-owner-protected-endpoint',
        token_value=access_token.access_token_value)

    # second `grant_type` `client_credential` call using token caching
    second_call = requests_mock.get('http://localhost/resource-owner-protected-endpoint2')
    beat_api_service.send_request(
        verb=HttpVerb.GET,
        url='http://localhost/resource-owner-protected-endpoint2'
    )

    assert second_call.last_request._request.headers['Authorization'] == 'Bearer credential_token', \
        'The last call should use access token acquired `grant_type` `client_credentials.`'
