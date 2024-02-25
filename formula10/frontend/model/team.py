from urllib.parse import quote

from formula10.database.model.db_team import DbTeam


class Team():
    @classmethod
    def from_db_team(cls, db_team: DbTeam):
        team: Team = cls()
        team.name = db_team.name
        return team

    def to_db_team(self) -> DbTeam:
        db_team: DbTeam = DbTeam(name=self.name)
        return db_team

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Team):
            return self.name == __value.name

        return NotImplemented

    name: str

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

NONE_TEAM: Team = Team()
NONE_TEAM.name = "None"