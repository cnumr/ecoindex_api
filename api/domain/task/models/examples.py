example_daily_limit_response = {
    "description": "You have reached the daily limit",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "daily_limit_per_host": 1,
                    "limit": 1,
                    "host": "www.ecoindex.fr",
                    "latest_result": {
                        "width": 1920,
                        "height": 1080,
                        "size": 107.178,
                        "requests": 6,
                        "score": 87,
                        "water": 1.89,
                        "date": "2023-01-05T12:06:57",
                        "id": "be8c3612-545f-4e72-8880-13b8db74ff6e",
                        "version": 1,
                        "initial_ranking": 1,
                        "url": "https://www.ecoindex.fr",
                        "nodes": 201,
                        "grade": "A",
                        "ges": 1.26,
                        "ecoindex_version": "5.4.1",
                        "page_type": None,
                        "host": "www.ecoindex.fr",
                        "initial_total_results": 1,
                    },
                    "message": (
                        "You have already reached the daily limit of 1 "
                        "requests for host www.ecoindex.fr today"
                    ),
                }
            }
        }
    },
}
