from sqlalchemy.orm import Session

from .....domain.user_auth.implementation.queries.is_registered import IsUserRegisteredQuery

from .....infrastructure.models.user import UserModel

class IsUserRegisteredQueryImpl(IsUserRegisteredQuery):
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, login):
        user_model = self.session.query(UserModel).filter(UserModel.login==login).one_or_none()
        return user_model != None