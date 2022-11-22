from fabelcommon.api_service import ApiService


class FeedApiService(ApiService):
    BASE_URL: str = 'https://lydbokforlaget-feed.isysnet.no'

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(
            client_id,
            client_secret,
            self.BASE_URL,
            '/token-server/oauth/token')
