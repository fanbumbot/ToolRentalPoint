from typing import Hashable, Callable, Iterable, Union

class EntityCQImpl:
    def __init__(
        self,
        implementations: dict[type, Callable]
    ):
        self.implementations = implementations

    def validate_from_domain(self, required_implementations: Iterable[type]):
        keys = self.implementations.keys()
        for impl in required_implementations:
            if impl not in keys:
                raise ValueError(f"Implementation of {impl.__name__} does not exist")
            
    def call(self, needed_command_or_query: type, *args, **kwargs):
        if needed_command_or_query not in self.implementations:
            raise ValueError(f"Implementation of {needed_command_or_query.__name__} does not exist")
        
        return self.implementations[needed_command_or_query](*args, **kwargs)


class Entity:
    def __init__(
        self,
        id: Hashable,
        impl: Union[EntityCQImpl, None]
    ):
        self.id = id
        self.impl = impl

    @classmethod
    def create(cls, *args) -> "Entity":
        pass
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, value):
        return (isinstance(value, self.__class__) and 
                value.id == self.id)
