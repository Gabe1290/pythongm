# Shipped into a Kivy export as microbit_sim/state.py (Stage P, unit K3).
# layout.py is shipped verbatim and imports option_of from here; an exported
# object has no object_data, so only the instance attribute is read.


def option_of(instance, name, default=None):
    value = getattr(instance, name, None)
    return default if value is None else value
