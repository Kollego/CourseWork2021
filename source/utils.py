def parse_timestamp(timestamp):
    hours = str(timestamp//3600).zfill(2)
    mins = str(timestamp%3600//60).zfill(2)
    secs = str(timestamp%60).zfill(2)
    return f"{hours}:{mins}:{secs}"
