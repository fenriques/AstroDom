
def format_seconds( seconds, format = "hms"):
    if seconds is None or seconds == "": return ""
    intervals = (
        ('h', 3600),    # 60 * 60
        ('m', 60),
        ('s', 1),
    )
    seconds = int(seconds)
    # Filter intervals based on the format variable
    intervals = [interval for interval in intervals if interval[0] in format]

    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value}{name}")

    return ' '.join(result)

def format_file_size(size):
    if size is None or size == "": return ""
    size = float(size)
    intervals = (
        ('GB', 1024),
        ('MB', 1),
    )

    for name, count in intervals:
        value = size / count
        if value >= 1:
            return f"{value:.2f} {name}"

    return f"{size} B"
