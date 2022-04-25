from json import dumps

from api.main import app

openapi = app.openapi()

print(dumps(openapi, indent=2, sort_keys=True))
