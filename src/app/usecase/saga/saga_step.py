from sqlalchemy.orm import Session

from abc import ABC

from ...domain.entity import EntityCQImpl

class SagaStep(ABC):
    def __init__(
        self,
        session: Session,
        impl: EntityCQImpl
    ):
        self.session = session
        self.impl = impl
    def __call__(self):
        raise NotImplementedError