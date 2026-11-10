"""
PA 7 dependency: paste in YOUR OWN completed PA 6 frames.py here.

Original header preserved below for reference:

PA 6: The Activation Record -- starter.

Complete ActivationRecord and CallStack below. See
PA_06_The_Activation_Record.md, Part B, for the full requirements.

Note on scope: PA1-5 never added function-call SYNTAX to USILang's
grammar (deliberately -- see PA5's pipeline-context note). PA6's
Part B interface is pure Python classes with no mention of parser
changes either, so test_frames.py drives ActivationRecord/CallStack
directly in Python (simulating what a parsed function call sequence
would do) rather than parsing real USILang function syntax. Your job
this week is the frame model itself, not a grammar extension.
"""

from typing import Dict, List, Optional

from symtable import Environment


class ActivationRecord:
    def __init__(
        self,
        function_name: str,
        parameters: Dict[str, object],
        locals_env: Environment,
        return_address: str,
        static_link: Optional["ActivationRecord"],
        dynamic_link: Optional["ActivationRecord"],
    ) -> None:
        # Storing all six arguments as attributes of the same names
        self.function_name = function_name
        self.parameters = parameters
        self.locals_env = locals_env
        self.return_address = return_address
        self.static_link = static_link
        self.dynamic_link = dynamic_link


class CallStack:
    def __init__(self) -> None:
        # Empty list holding activation records
         self._frames: List[ActivationRecord] = []

    def push(self, record: ActivationRecord) -> None:
        # Adds activation record to the top of the stack
        self._frames.append(record)

    def pop(self) -> ActivationRecord:
        """Remove and return the top frame."""
        record = self._frames.pop()
        record.locals_env.release(getattr(record, "borrowed_cells", ()))
        return record

    def current(self) -> ActivationRecord:
        """Return (without removing) the top frame."""
        return self._frames[-1]

    def trace(self) -> List[str]:
        """
        Return one formatted string per live frame, BOTTOM of the
        stack first (oldest call first). Format is up to you, but
        each line must include the function_name and its parameters.
        """
        # List showing every frame from oldest to newest
        return [
            f"{record.function_name} {record.parameters}"
            for record in self._frames
        ]
