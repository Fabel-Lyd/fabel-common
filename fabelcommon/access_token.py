from datetime import datetime, timedelta
from typing import Optional


class AccessToken:
    def __init__(
            self,
            access_token_value: str,
            expires_in: int,
            user_id: Optional[str]
    ):
        self.__access_token_value = access_token_value
        self.__user_id = user_id

        current_time = datetime.now()
        self.__expires_at = current_time + timedelta(seconds=expires_in)

    @property
    def access_token_value(self) -> str:
        return self.__access_token_value

    @property
    def user_id(self) -> Optional[str]:
        return self.__user_id

    @property
    def is_valid(self) -> bool:
        return self.__expires_at > datetime.now()
