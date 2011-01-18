def flatten_choices(choices):
    """Flattened version of choices tuple."""
    flat = []
    for choice, value in choices:
        if isinstance(value, (list, tuple)):
            flat.extend(value)
        else:
            flat.append((choice,value))
    return flat


def pick_choice(choices, value):
    return dict(flatten_choices(choices))[value]
