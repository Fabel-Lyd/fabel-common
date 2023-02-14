from fabelcommon.feed.feed_api_service import FeedApiService


def test_feed_access_token_key():
    access_token_key = FeedApiService(
        'test_client_id',
        'test_client_secret'
    )._access_token_key

    assert access_token_key.value == 'access_token'


def test_feed_request_data():
    feed_request_data = FeedApiService(
        'test_client_id',
        'test_client_secret')._token_request_data

    assert feed_request_data == {'grant_type': 'client_credentials'}


def test_feed_request_auth():
    feed_request_auth = FeedApiService(
        'test_client_id',
        'test_client_secret')._token_request_auth

    assert feed_request_auth == ('test_client_id', 'test_client_secret')


def test_feed_create_header():
    feed_header = FeedApiService(
        'test_client_id',
        'test_client_secret')._create_authorization_header('test_token')

    assert feed_header == {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }
