from urllib.parse import quote

from formula10.database.model.db_team import DbTeam


class Team:
    @classmethod
    def from_db_team(cls, db_team: DbTeam):
        team: Team = cls()
        team.id = db_team.id
        team.name = db_team.name
        return team

    def to_db_team(self) -> DbTeam:
        db_team: DbTeam = DbTeam(id=self.id)
        db_team.name = self.name
        return db_team

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Team):
            return self.id == __value.id

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)

    id: int
    name: str

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

NONE_TEAM: Team = Team()
NONE_TEAM.id = 0
NONE_TEAM.name = "None"