class QuotaExceededException(Exception):
    def __init__(self, limit: int, host: str) -> None:
        self.limit = limit
        self.host = host
        self.message = f"You have already reached the daily limit of {limit} requests for host {host} today"

        super().__init__(self.message)
