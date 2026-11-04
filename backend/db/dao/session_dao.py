from db.dao.basedao import BaseDao
from db.models import Session


class SessionDao(BaseDao):
    model = Session
