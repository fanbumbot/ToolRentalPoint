from sqlalchemy.orm import Session

from .saga import Saga, SagaStep

class CreateSaga(Saga):
    def __init__(
        self,
        steps: list[SagaStep],
        session: Session,
        model
    ):
        super().__init__(steps)
        self.session = session
        self.model = model

    def __call__(self):
        super().__call__()
        self.session.add(self.model)
        self.session.flush([self.model])