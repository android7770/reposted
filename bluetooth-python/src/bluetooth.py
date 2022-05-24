from typing import Any, Callable, Dict, NoReturn

import objc
from logger import logger


def _fail(message: str) -> NoReturn:
    logger.critical(message)
    raise RuntimeError(message)


bundle = objc.loadBundle(
    'IOBluetooth',
    globals(),  # noqa: WPS421
    bundle_path=objc.pathForFramework(
        '/System/Library/Frameworks/IOBluetooth.framework',
    ),
)
if not bundle:
    raise RuntimeError('Failed to load IOBluetooth framework')

# Request handles to functions:
function_specs = [
    ('IOBluetoothPreferenceGetControllerPowerState', b'oI'),
    ('IOBluetoothPreferenceSetControllerPowerState', b'vI'),
]
namespace: Dict[str, Any] = {}
objc.loadBundleFunctions(bundle, namespace, function_specs)

# Cid we get everything we need?
for function_name, _ in function_specs:
    if function_name not in namespace:
        _fail('Failed to load: {0}'.format(function_name))

_bs_getter: Callable[[], int] = namespace[function_specs[0][0]]
_bs_setter: Callable[[int], int] = namespace[function_specs[1][0]]


def toggle_bluetooth_state() -> int:
    """Turn on if turned off and vice a versa."""
    current_state = _bs_getter()
    new_state = _next_state(current_state)
    _bs_setter(new_state)
    return new_state


def get_bluetooth_state() -> int:
    """Returns 0 or 1 state. Where 1 is 'turned on'."""
    return _bs_getter()


def _next_state(current: int) -> int:
    if current == 1:
        return 0
    return 1
