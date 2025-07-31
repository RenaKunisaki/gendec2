from __future__ import annotations

class Mutator:
    """Makes random changes to C source code.
    Base class for mutators.
    """

    def __init__(self, coll:MutatorCollection):
        self.collection = coll

    def mutate(self, code:str) -> str:
        """Modify the given code."""
        raise NotImplementedError
