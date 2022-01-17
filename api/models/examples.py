example_exception_response = {
    "description": "My bad! :( => Server exception",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "args": [
                        "unknown error: net::ERR_NAME_NOT_RESOLVED\n  (Session info: headless chrome=96.0.4664.110)",
                        [
                            "#0 0x55ffa3dd7ee3 <unknown>",
                            "#1 0x55ffa38a5608 <unknown>",
                        ],
                    ],
                    "exception": "WebDriverException",
                    "message": "unknown error: net::ERR_NAME_NOT_RESOLVED\n  (Session info: headless chrome=96.0.4664.110)",
                }
            }
        }
    },
}
