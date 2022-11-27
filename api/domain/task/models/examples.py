example_daily_limit_response = {
    "description": "You have reached the daily limit",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "message": "You have already reached the daily limit of 5 requests for host www.ecoindex.fr today",
                    "daily_limit_per_host": 5,
                    "host": "www.ecoindex.fr",
                }
            }
        }
    },
}
