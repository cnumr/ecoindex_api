from api.models.responses import WorkerHealth, WorkersHealth
from worker.tasks import app


def is_worker_healthy():
    workers = []
    workers_ping = app.control.ping()

    for worker in workers_ping:
        for name in worker:
            workers.append(
                WorkerHealth(name=name, healthy=True if "ok" in worker[name] else False)
            )

    result = WorkersHealth(
        healthy=False if False in [w.healthy for w in workers] else True,
        workers=workers,
    )

    return {"workers": result}
