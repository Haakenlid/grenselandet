def extended_blank_lines(logical_line,
                         blank_lines,
                         indent_level,
                         previous_logical):
    """Check for missing blank lines after class declaration."""
    if previous_logical.startswith('class '):
        if (
            logical_line.startswith(('def ', 'class ', '@')) or
            pep8.DOCSTRING_REGEX.match(logical_line)
        ):
            if indent_level and not blank_lines:
                yield (0, 'E309 expected 1 blank line after class declaration')
    elif previous_logical.startswith('def '):
        if blank_lines and pep8.DOCSTRING_REGEX.match(logical_line):
            yield (0, 'E303 too many blank lines ({0})'.format(blank_lines))
    elif pep8.DOCSTRING_REGEX.match(previous_logical):
        # Missing blank line between class docstring and method declaration.
        if (
            indent_level and
            not blank_lines and
            logical_line.startswith(('def ')) and
            '(self' in logical_line
        ):
            yield (0, 'E301 expected 1 blank line, found 0')
pep8.register_check(extended_blank_lines)