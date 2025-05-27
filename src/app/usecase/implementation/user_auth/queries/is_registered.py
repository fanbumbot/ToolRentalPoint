from sqlalchemy.orm import Session

from .....domain.user_auth.implementation.queries.is_registered import IsUserRegisteredQuery, Login

from .....infrastructure.models.user import UserModel

class IsUserRegisteredQueryImpl(IsUserRegisteredQuery):
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, login: Login):
        user_model = self.session.query(UserModel).filter(UserModel.login==login.value).one_or_none()
        return user_model != None