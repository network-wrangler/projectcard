import datetime
from datetime import time
from typing import Annotated, Any, List

from pydantic import Field
from pydantic.dataclasses import dataclass


class TimeFormatError(Exception):
    pass


class TimespanFormatError(Exception):
    pass


PC_TimeString = Annotated[str, Field(pattern=r"^\d{2}:\d{2}(:\d{2})?$")]
PC_TimeSpanString = Annotated[List[PC_TimeString], Field(min_length=2, max_length=2)]


@dataclass
class PC_Time:
    time: PC_TimeString

    @property
    def datetime(self):
        if type(self.time) == str:
            if len(self.time.split(":")) == 2:
                return datetime.datetime.strptime(self.time, "%H:%M")
            else:
                return datetime.datetime.strptime(self.time, "%H:%M:%S")
        elif type(self.time) == time:
            return self.time
        else:
            raise TimeFormatError("time must be a string or time object")

    @property
    def time_sec(self):
        return self.datetime.hour * 3600 + self.datetime.minute * 60 + self.datetime.second


@dataclass
class PC_Timespan:
    timespan: PC_TimeSpanString

    @property
    def start_time(self):
        return self.timespan[0].time

    @property
    def end_time(self):
        return self.timespan[1].time

    @property
    def start_time_dt(self):
        return self.timespan[0].datetime

    @property
    def end_time_dt(self):
        return self.timespan[1].datetime

    @property
    def duration_dt(self):
        """Returns a datetime.timedelta object representing the duration of the timespan.

        If end_time is less than start_time, the duration will assume that it crosses over
        midnight.
        """
        if self.end_time_dt < self.start_time_dt:
            return datetime.timedelta(
                hours=24 - self.start_time_dt.hour + self.end_time_dt.hour,
                minutes=self.end_time_dt.minute - self.start_time_dt.minute,
                seconds=self.end_time_dt.second - self.start_time_dt.second,
            )
        else:
            return self.end_time_dt - self.start_time_dt

    @property
    def start_time_sec(self):
        """Start time in seconds since midnight."""
        return self.timespan[0].time_sec

    @property
    def end_time_sec(self):
        """End time in seconds since midnight."""
        return self.timespan[1].time_sec

    @property
    def duration_sec(self):
        """Duration of timespan in seconds.

        If end_time is less than start_time, the duration will assume that it crosses over
        midnight.
        """
        if self.end_time_sec < self.start_time_sec:
            return (24 * 3600) - self.start_time_sec + self.end_time_sec
        else:
            return self.end_time_sec - self.start_time_sec
