from . import detector

def detect(*args, **kwargs):
    return detector.detect(*args, **kwargs)

def to_time_string(*args, **kwargs):
    return detector.to_time_string(*args, **kwargs)