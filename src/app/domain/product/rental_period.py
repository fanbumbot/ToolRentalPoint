from dataclasses import dataclass
from datetime import datetime, timedelta

from ..validation import type_validate

class StartIsGreaterThanEndError(ValueError):
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

class NegativeDurationError(ValueError):
    pass

@dataclass(frozen=True)
class RentalPeriodDuration:
    duration: timedelta

    def __post_init__(self):
        type_validate(self.duration, "Duration", timedelta)

        if self.duration < timedelta():
            raise NegativeDurationError

@dataclass(frozen=True)
class RentalPeriod:
    start: datetime
    end: datetime

    def __post_init__(self):
        type_validate(self.start, "Start of the rental period", datetime)
        type_validate(self.end, "End of the rental period", datetime)

        if self.start > self.end:
            raise StartIsGreaterThanEndError(self.start, self.end)
        
    def get_duration(self):
        return RentalPeriodDuration(self.end-self.start)
