from pydantic import ValidationError
from pytest import raises

from api.models.responses import ApiHealth, WorkerHealth, WorkersHealth


def test_model_apihealth_valid():
    valid_health = ApiHealth(
        database=True,
        workers=WorkersHealth(
            healthy=True,
            workers=[
                WorkerHealth(name="celery@1b65f3fe0282", healthy=True),
                WorkerHealth(name="celery@eceffdacd662", healthy=True),
            ],
        ),
    )
    assert valid_health.workers.healthy == True
    assert valid_health.database == True


def test_model_apihealth_empty():
    expected_errors = [
        {"loc": ("database",), "msg": "field required", "type": "value_error.missing"},
        {
            "loc": ("workers",),
            "msg": "field required",
            "type": "value_error.missing",
        },
    ]
    with raises(ValidationError) as error:
        ApiHealth()
        assert error.errors == expected_errors


def test_model_apihealth_invalid():
    expected_errors = [
        {
            "loc": ("database",),
            "msg": "value could not be parsed to a boolean",
            "type": "type_error.bool",
        },
        {
            "loc": ("workers",),
            "msg": "value could not be parsed to a boolean",
            "type": "type_error.bool",
        },
    ]
    with raises(ValidationError) as error:
        ApiHealth(database="An error message", workers=1.2)
        assert error.errors == expected_errors
