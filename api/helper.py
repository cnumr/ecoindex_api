def format_exception_response(exception: Exception) -> str:
    return (
        f"Woops! My bad! :( => Error type: {type(exception).__name__}"
        f"{'. Args: '+ ''.join(exception.args) if exception.args else ''}"
        f"{'. Message: ' + exception.msg if hasattr(exception, 'msg') else ''}"
    )
