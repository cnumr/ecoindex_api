from pydantic import ValidationError
from pytest import raises

from api.models.responses import ApiHealth


def test_model_apihealth_valid():
    valid_health = ApiHealth(
        database=True,
        workers=[
            {"celery@1b65f3fe0282": {"ok": "pong"}},
            {"celery@eceffdacd662": {"ok": "pong"}},
        ],
    )
    assert len(valid_health.workers) == 2
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
