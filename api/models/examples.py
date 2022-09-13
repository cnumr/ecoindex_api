example_exception_response = {
    "description": "My bad! 😕 => Server exception",
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

example_exception_ERR_NAME_NOT_RESOLVED_response = {
    "description": "This url seems not OK... 🙄",
    "content": {
        "application/json": {
            "example": {
                "detail": "This host is unreachable. Are you really sure of this url? 🤔"
            }
        }
    },
}

example_exception_ERR_CONNECTION_TIMED_OUT_response = {
    "description": "Timeout reached when requesting this url. This is probably a temporary issue. 😥",
    "content": {
        "application/json": {
            "example": {
                "detail": "Timeout reached when requesting this url. This is probably a temporary issue. 😥"
            }
        }
    },
}


example_file_not_found = {
    "description": "Not found",
    "content": {
        "application/json": {
            "example": {
                "detail": "File at path screenshots/v0/550cdf8c-9c4c-4f8a-819d-cb69d0866fe1.png does not exist."
            }
        }
    },
}
