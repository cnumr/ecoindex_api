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
                "detail": "File at path screenshots/v0/550cdf8c-9c4c-4f8a-819d-cb69d0866fe1.webp does not exist."
            }
        }
    },
}

example_exception_HTTP_520_ECOINDEX_TYPE_ERROR_response = {
    "description": "The mimetype of the analyzed resource is not 'text/html'",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "mimetype": "text/css",
                    "message": "This resource is not a standard page with mimeType 'text/html'",
                }
            }
        }
    },
}

example_exception_HTTP_521_ECOINDEX_CONNECTION_ERROR_response = {
    "description": "The analyzed webpage responded with an error status code",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "status": 401,
                    "message": "This page can not be analyzed because the response status code is not 200",
                }
            }
        }
    },
}
