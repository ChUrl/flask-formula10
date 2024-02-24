from formula10.database.model.race_result import RaceResult
from formula10.database.model.user import User
from formula10 import db

def race_has_result(race_name: str) -> bool:
    return db.session.query(RaceResult).filter_by(race_name=race_name).first() is not None


def user_exists(user_name: str) -> bool:
    return db.session.query(User).filter_by(name=user_name).first() is not None