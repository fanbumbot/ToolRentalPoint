from .saga_step import SagaStep

class Saga:
    def __init__(
        self,
        steps: list[SagaStep]
    ):
        self.steps = steps

    def __call__(self):
        for step in self.steps:
            try:
                step.__call__()
            except Exception:
                raise