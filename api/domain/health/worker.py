from worker.tasks import app


def is_worker_healthy():
    return {"workers": app.control.ping()}
