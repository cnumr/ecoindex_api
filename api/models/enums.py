from enum import Enum


class Version(Enum):
    v0 = "v0"
    v1 = "v1"

    def get_version_number(self):
        return self.value[1:]
