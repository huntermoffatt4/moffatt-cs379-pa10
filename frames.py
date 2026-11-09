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
        # TODO: store all six arguments as attributes of the same names.
        raise NotImplementedError


class CallStack:
    def __init__(self) -> None:
        # TODO: internal storage for the stack of frames.
        raise NotImplementedError

    def push(self, record: ActivationRecord) -> None:
        # TODO
        raise NotImplementedError

    def pop(self) -> ActivationRecord:
        """Remove and return the top frame."""
        # TODO
        raise NotImplementedError

    def current(self) -> ActivationRecord:
        """Return (without removing) the top frame."""
        # TODO
        raise NotImplementedError

    def trace(self) -> List[str]:
        """
        Return one formatted string per live frame, BOTTOM of the
        stack first (oldest call first). Format is up to you, but
        each line must include the function_name and its parameters.
        """
        # TODO
        raise NotImplementedError
