from typing import Dict, Any, Iterator, Optional
from collections import abc
from types import FunctionType
import inspect

# This class is a DynamicScope. It is a mapping from strings to values.
# It is used to look up the values of variables in the calling function.
class DynamicScope(abc.Mapping):
    def __init__(self):
        self.env: Dict[str, Optional[Any]] = {}
    
    # This is the method that is called when you look up a value in the DynamicScope.
    # It raises a NameError if the key is not in the DynamicScope.
    # It raises an UnboundLocalError if the value is '__unbound__'.
    def __getitem__(self, key: str) -> Optional[Any]:
        if key not in self.env:
            raise NameError(f"Name '{key}' is not defined.")
        if self.env[key] == '__unbound__':
            raise UnboundLocalError(f"Name '{key}' was referenced before assignment.")
        return self.env[key]

    # This is the method that is called when you assign a value to a key in the DynamicScope.
    # It adds the key-value pair to the DynamicScope.
    def __setitem__(self, key: str, value: Optional[Any]):
        if key not in self.env:
            self.env[key] = value

    # This is the method that is called when you iterate over the DynamicScope.
    # It returns an iterator over the keys of the DynamicScope.
    def __iter__(self) -> Iterator[str]:
        return iter(self.env)

    # This is the method that is called when you get the length of the DynamicScope.
    # It returns the length of the DynamicScope.
    def __len__(self) -> int:
        return len(self.env)
    
    def __contains__(self, key: str) -> bool:
        return key in self.env


# The way this works is that we use the inspect module to get the stack frame
# of the calling function. We then use the frame to get the local variables
# and free variables. We then use the local variables to populate the
# DynamicScope. We then use the free variables to populate the DynamicScope
# with '__unbound__' as a placeholder value. We then return the DynamicScope.
# The DynamicScope is then used to look up the values of the variables.
# If the value is '__unbound__', then we raise an UnboundLocalError.
# If the value is not '__unbound__', then we return the value.
# If the key is not in the DynamicScope, then we raise a NameError.

def get_dynamic_re() -> DynamicScope:
    dyn_scope = DynamicScope()
    stack = inspect.stack()[1:]

    # This iterates over the stack frames
    for frame_info in stack:
        frame = frame_info.frame
        free_vars = list(frame.f_code.co_freevars)

        # This iterates over the local variables and adds them to the local_vars dict
        # if they are not in the free variables.
        local_vars = {}
        for var_name, var_value in frame.f_locals.items():
            if var_name not in free_vars:
                local_vars[var_name] = var_value

        # This iterates over the local variables and adds/overwrites them to the DynamicScope
        for var_name, var_value in local_vars.items():
            dyn_scope[var_name] = var_value

        # This iterates over the free variables and adds them to the DynamicScope
        # with the value '__unbound__' if they are not already in the DynamicScope.
        all_vars = frame.f_code.co_cellvars + frame.f_code.co_varnames
        if not len(frame.f_locals) and len(all_vars):
            for var in all_vars:
                dyn_scope[var] = '__unbound__'

    return dyn_scope
