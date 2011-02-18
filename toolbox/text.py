def smartish_split(string):
    """Generator that splits a string by spaces, preserving quoted bits.
    Quotes cannot be escaped and are terminated automatically 
    when the end of the string is reached.
    Quoted bits are returned without their surrounding quotes."""
    SPACE = ' '
    QUOTE = '"'
    buffer = ''
    is_inside_quote = False
    
    for c in string.strip():
        if c == QUOTE:
            if is_inside_quote:
                is_inside_quote = False
                yield buffer
                buffer = ''
            else:
                is_inside_quote = True
        elif c == SPACE and not is_inside_quote:
            if buffer:
                yield buffer
            buffer = ''
        else:
            buffer += c
    
    if buffer:
        yield buffer
