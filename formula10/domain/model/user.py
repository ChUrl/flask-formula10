from urllib.parse import quote

from formula10.database.model.db_user import DbUser


class User():
    @classmethod
    def from_db_user(cls, db_user: DbUser):
        user: User = cls()
        user.id = db_user.id
        user.name = db_user.name
        user.enabled = db_user.enabled
        return user

    def to_db_user(self) -> DbUser:
        db_user: DbUser = DbUser(id=self.id)
        db_user.name = self.name
        db_user.enabled = self.enabled
        return db_user

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, User):
            return self.id == __value.id

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)

    id: int
    name: str
    enabled: bool

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)
