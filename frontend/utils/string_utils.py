def safe_format(template, **kwargs):
    """
    Safely format strings without f-string syntax issues.
    """
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError) as e:
        return f"Error in string formatting: {str(e)}"


def safe_fstring(template, **kwargs):
    """
    Safely format f-strings by handling special characters.
    """
    try:
        # Replace problematic characters
        template = template.replace("\\", "\\\\")
        template = template.replace('"', '\\"')
        template = template.replace("'", "\\'")

        # Format the string
        return eval(f'f"{template}"', kwargs)
    except Exception as e:
        return f"Error in f-string formatting: {str(e)}"
