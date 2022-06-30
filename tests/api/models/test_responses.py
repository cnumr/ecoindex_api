from api.models.responses import ApiHealth
from pydantic import ValidationError
from pytest import raises


def test_model_apihealth_valid():
    valid_health = ApiHealth(database=True, chromedriver=True)
    assert valid_health.chromedriver == True
    assert valid_health.database == True


def test_model_apihealth_empty():
    expected_errors = [
        {"loc": ("database",), "msg": "field required", "type": "value_error.missing"},
        {
            "loc": ("chromedriver",),
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
            "loc": ("chromedriver",),
            "msg": "value could not be parsed to a boolean",
            "type": "type_error.bool",
        },
    ]
    with raises(ValidationError) as error:
        ApiHealth(database="An error message", chromedriver=1.2)
        assert error.errors == expected_errors
