#!/usr/bin/env python3
"""The simulated radio between micro:bits in one room (Stage S9).

Pure. Each board queues what it sends in its own outbox
(``MicrobitSimulator.radio_send``); ``deliver`` moves every outbox to the
*other* boards that are in the same group, once per frame, ahead of the
boards' own updates. A board never hears itself, and a board in a different
group hears nothing -- as on the device. There is no global bus: delivery is
between the boards handed in, so a room change or a new game starts clean.
"""

MIN_GROUP = 0
MAX_GROUP = 255
MAX_MESSAGE = 32            # MicroPython's default radio payload (characters)


def clamp_group(value):
    try:
        group = int(float(value))
    except (TypeError, ValueError):
        return MIN_GROUP
    return max(MIN_GROUP, min(MAX_GROUP, group))


def clean_message(value):
    """What goes over the air: numbers stay numbers, anything else becomes
    text cut to the 32-character payload."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    return str(value)[:MAX_MESSAGE]


def as_number(value):
    """A received value as a number, ``0`` if it isn't one."""
    if isinstance(value, (int, float)):
        return value
    try:
        number = float(str(value).strip())
    except ValueError:
        return 0
    return int(number) if number.is_integer() else number


def deliver(sims):
    """Move every board's outbox to the other boards in its group.
    Returns how many messages were delivered (counting each recipient)."""
    delivered = 0
    for sender in sims:
        messages = sender.take_radio_outbox()
        if not messages:
            continue
        for receiver in sims:
            if receiver is sender or receiver.radio_group != sender.radio_group:
                continue
            for message in messages:
                receiver.radio_receive(message)
                delivered += 1
    return delivered
