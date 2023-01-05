from api.domain.ecoindex.models.responses import ApiEcoindex


class QuotaExceededException(Exception):
    def __init__(self, limit: int, host: str, latest_result: ApiEcoindex) -> None:
        self.limit = limit
        self.host = host
        self.latest_result = latest_result
        self.message = f"You have already reached the daily limit of {limit} requests for host {host} today"

        super().__init__(self.message)
