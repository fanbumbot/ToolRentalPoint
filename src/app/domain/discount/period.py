from datetime import datetime
from dataclasses import dataclass

from ..validation import type_validate

@dataclass(frozen=True)
class Period:
    start_datetime: datetime
    end_datetime: datetime

    def __post_init__(self):
        type_validate(self.start_datetime, "Start of discount season", datetime)
        type_validate(self.end_datetime, "End of discount season", datetime)
        if self.start_datetime > self.end_datetime:
            raise ValueError("Start period must be before end period")
        
    def is_belonged_to_period(self, timestamp: datetime):
        return timestamp > self.start_datetime and timestamp < self.end_datetime