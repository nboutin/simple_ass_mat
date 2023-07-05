"""
:author Nicolas Boutin
:date 2023-07-05
"""
# pylint: disable=logging-fstring-interpolation

import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)


class ScheduleError (ValueError):
    pass


class Schedule:
    """
    Schedule / planning, hour, day, week, month, year
    """
    day_id_t = int
    hour_range_t = dict[str, str]
    days_t = dict[day_id_t, hour_range_t]

    week_id_t = int
    week_day_t = str  # monday, tuesday, wednesday, thursday, friday, saturday, sunday
    weeks_t = dict[week_id_t, dict[week_day_t, day_id_t]]

    week_range_t = list[dict[str, int]]
    year_t = dict[week_id_t, week_range_t]

    def __init__(self, year: year_t, weeks: weeks_t, days: days_t, paid_vacation: week_range_t):
        self._year = year
        self._weeks = weeks
        self._days = days
        self._paid_vacation = paid_vacation

        self._check_input_data()

    def get_working_week_count(self) -> int:
        """brief Count working week for a complete year"""
        week_count = 0
        for week_id in self._year.keys():
            week_count += self._get_working_week_count(week_id)

        logger.debug(f"working week count = {week_count}")
        return week_count

    def _get_working_week_count(self, week_id: week_id_t) -> int:
        """Count working week for a given week_id"""
        week_count: int = 0
        for week_range in self._year[week_id]:
            start = week_range['start']
            end = week_range['end']
            week_count += end - start + 1
        return week_count

    def get_paid_vacation_week_count(self) -> int:
        """
        :brief Count week of paid vacation
        """
        week_count = 0
        for week_range in self._paid_vacation:
            start = week_range['start']
            end = week_range['end']
            week_count += end - start + 1

        logger.debug(f"paid vacation week count = {week_count}")
        return week_count

    def get_working_hour_per_week(self, week_id: int = 0) -> float:
        """Calculate working hour per week"""
        hour_count = 0
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            day_id = self._weeks[week_id][day]
            hour_count += self.get_working_hour_per_day(day_id)

        logger.debug(f"working hour per week = {hour_count}")
        return hour_count

    def get_working_hour_per_day(self, day_id: int) -> float:
        """Calculate working hour per day"""
        hour_count: float = 0.0
        if day_id is None:
            return hour_count

        for id_, time_ in self._days.items():
            if id_ == day_id:
                start = datetime.strptime(time_['start'], '%H:%M')
                end = datetime.strptime(time_['end'], '%H:%M')
                hour_count: float = (end - start).seconds / 3600.0

        logger.debug(f"working hour per day = {hour_count}")
        return hour_count

    def get_working_hour_per_month(self) -> float:
        """Calculate working hour per month"""
        hour_per_week_count: float = 0.0
        for week_id in self._year.keys():
            # working_week_count = self._get_working_week_count(week_id)
            hour_per_week_count += self.get_working_hour_per_week(
                week_id) * 52

        return hour_per_week_count / 12

    def get_working_hour_per_month_normalized(self) -> int:
        """<0.5, round down, >0.5, round up"""
        return round(self.get_working_hour_per_month())

    def get_working_day_per_week(self, week_id: int = 0) -> float:
        """working day count per week"""
        working_day_count = 0
        for day_id in self._weeks[week_id].values():
            if day_id is not None:
                working_day_count += 1
        return working_day_count

    def get_working_day_per_month(self) -> float:
        """day_per_week_count * 52 / 12"""
        return self.get_working_day_per_week() * 52 / 12

    def get_working_day_per_month_normalized(self) -> int:
        """always round up"""
        return math.ceil(self.get_working_day_per_month())

    def _check_input_data(self) -> None:
        """
        Check that:
        - total number of week(working and paid vacation) is less or equal to 52
        - total number of working week is less or equal to 47
        - total number of paid vacation week is less or equal to 5
        """

        working_week_count = self.get_working_week_count()
        paid_vacation_week_count = self.get_paid_vacation_week_count()

        if working_week_count + paid_vacation_week_count > 52:
            raise ScheduleError(
                "Total number of week(working and paid vacation) is more than 52")

        if working_week_count > 47:
            raise ScheduleError("Total number of working week is more than 47")

        if paid_vacation_week_count > 5:
            raise ScheduleError(
                "Total number of paid vacation week is more than 5")