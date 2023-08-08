"""
:author Nicolas Boutin
:date 2023-07
"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=no-else-return

import logging
import datetime
import calendar

from . import helper
from .planning_jour import PlanningJour, JourIdError

logger = logging.getLogger(__name__)


class PlanningError (ValueError):
    """Planning error"""


class WeekIdError(ValueError):
    """Week id error"""


class Planning:
    """
    Planning / planning, hour, day, week, month, year
    """
    _COMPLETE_YEAR_WORKING_WEEK_COUNT = 47
    _COMPLETE_YEAR_PAID_VACATION_WEEK_COUNT = 5

    week_id_t = int
    week_day_t = str  # lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche
    weeks_t = dict[week_id_t, dict[week_day_t, PlanningJour.jour_id_t]]

    week_range_t = list[dict[str, int]]
    year_t = dict[week_id_t, week_range_t]

    def __init__(self, jours: PlanningJour, annee: year_t, semaines: weeks_t, conges_payes: week_range_t):
        self._jours = jours
        self._year = annee
        self._weeks = semaines
        self._conges_payes = conges_payes

        self._check_input_data()

    def is_annee_complete(self) -> bool:
        """Evaluate if contrat is for a complete year (47 week) or an incomplete year"""
        return (self.get_semaines_travaillees_annee() == Planning._COMPLETE_YEAR_WORKING_WEEK_COUNT) and \
            (self.get_semaines_conges_payes_annee() == Planning._COMPLETE_YEAR_PAID_VACATION_WEEK_COUNT)

    def get_semaines_travaillees_annee(self) -> int:
        """Count working week for a complete year"""
        week_count = 0
        for week_id in self._year.keys():
            week_count += self._get_semaines_travaillees_par_id(week_id)
        return week_count

    def _get_semaines_travaillees_par_id(self, week_id: week_id_t) -> int:
        """Compte nombre de semaine travaille pour week_id donné"""
        week_count: int = 0
        for week_ranges in self._year[week_id]:
            if len(week_ranges) == 1:
                week_count += 1
            elif len(week_ranges) == 2:
                week_count += week_ranges[1] - week_ranges[0] + 1
            else:
                raise PlanningError(f"week_range length is not 1 or 2 for id {week_id}")
        return week_count

    def get_semaines_conges_payes_annee(self) -> int:
        """Count week of paid vacation"""
        week_count = 0
        for week_ranges in self._conges_payes:
            if len(week_ranges) == 1:
                week_count += 1
            elif len(week_ranges) == 2:
                week_count += week_ranges[1] - week_ranges[0] + 1
            else:
                raise PlanningError("week_range length is not 1 or 2 for conges_payes")
        return week_count

    def get_heure_travaillees_semaine_par_date(self, year,  week_number: int) -> float:
        """Calculate working hour per week"""
        dates = helper.get_dates_in_week(year, week_number)
        week_id = self.get_semaine_id_par_date(dates[0])
        try:
            return self.get_heures_travaillees_semaine_par_id(week_id)
        except WeekIdError:
            return 0.0

    def get_heures_travaillees_semaine_par_id(self, semaine_id: int = 0) -> float:
        """Calculate working hour per week"""
        heures_travaillees = 0

        for jour_nom in calendar.day_name:
            try:
                jour_id = self._weeks[semaine_id][jour_nom]
                heures_travaillees += self._jours.get_heures_travaillees_par_jour_id(jour_id)
            except KeyError as key_error:
                raise WeekIdError(f"semaines_id {semaine_id} not found") from key_error
            except JourIdError:
                pass

        return heures_travaillees

    def get_heures_travaillees_jour_par_date(self, date: datetime.date) -> float:
        """Calculate working hour per day"""
        heures_travaillees = 0.0
        jour_id = self.get_jour_id_par_date(date)
        try:
            heures_travaillees = self._jours.get_heures_travaillees_par_jour_id(jour_id)
        except JourIdError:
            pass
        logger.debug(f"heures_travaillees_jour_par_date: {date} = {heures_travaillees}")
        return heures_travaillees

    def get_heures_travaillees_mois_mensualisees(self) -> float:
        """Calculate working hour per month"""
        heures_travaillees_annee: float = 0.0
        for week_id in self._year.keys():
            if self.is_annee_complete():
                heures_travaillees_semaine = self.get_heures_travaillees_semaine_par_id(week_id)
                semaines_travaillees_annee = self._get_semaines_travaillees_par_id(week_id)
                semaines_travaillees_annee = semaines_travaillees_annee * 52 / 47
                heures_travaillees_annee += heures_travaillees_semaine * semaines_travaillees_annee
            else:
                semaines_travaillees_annee = self._get_semaines_travaillees_par_id(week_id)
                heures_travaillees_annee += self.get_heures_travaillees_semaine_par_id(week_id) \
                    * semaines_travaillees_annee

        return heures_travaillees_annee / 12

    def get_jours_travailles_semaine_par_id(self, week_id: int = 0) -> float:
        """working day count per week"""
        working_day_count = 0
        for day_id in self._weeks[week_id].values():
            if day_id is not None:
                working_day_count += 1
        return working_day_count

    def get_jours_travailles_mois_mensualise(self) -> float:
        """day_per_week_count * 52 / 12"""
        if self.is_annee_complete():
            jours_travailles_annee = 0.0
            for semaine_id in self._weeks.keys():
                jours_travailles_annee += self.get_jours_travailles_semaine_par_id(semaine_id)
            return jours_travailles_annee * 52 / 12
        else:
            jours_travailles_annee = 0.0
            for semaine_id in self._weeks.keys():
                semaines_travaillees = self._get_semaines_travaillees_par_id(semaine_id)
                jours_travailles_semaine = self.get_jours_travailles_semaine_par_id(semaine_id)
                jours_travailles_annee += jours_travailles_semaine * semaines_travaillees
            return jours_travailles_annee / 12

    def get_jour_id_par_date(self, date: datetime.date):
        """Get jour_id par date"""
        week_id = self.get_semaine_id_par_date(date)
        weekday_string = date.strftime('%A').lower()
        try:
            day_id = self._weeks[week_id][weekday_string]
            return day_id
        except KeyError:
            return None

    def get_semaine_id_par_date(self, date: datetime.date):
        """Get week id from date"""
        week_number: int = int(date.strftime('%U'))
        for id_, week_ranges in self._year.items():
            for week_range in week_ranges:
                if len(week_range) == 1 and week_range[0] == week_number:
                    return id_
                elif len(week_range) == 2:
                    if week_range[0] <= week_number <= week_range[1]:
                        return id_
        return None

    def get_jours_travailles_planifies_mois_par_date(self, date: datetime.date) -> int:
        """Get working day count for a given month"""
        jour: int = 0
        dates = helper.get_dates_in_month(date)

        for i_date in dates:
            day_id = self.get_jour_id_par_date(i_date)
            if day_id is not None:
                jour += 1
        return jour

    def get_heures_travaillees_prevu_mois_par_date(self, date: datetime.date) -> float:
        """Get working hour planned for a month by date"""
        hour_count: float = 0.0
        dates = helper.get_dates_in_month(date)

        for i_date in dates:
            jour_id = self.get_jour_id_par_date(i_date)
            if jour_id is not None:
                hour_count += self._jours.get_heures_travaillees_par_jour_id(jour_id)
        return hour_count

    def avec_frais_repas_dejeuner_jour_par_date(self, date: datetime.date) -> bool:
        """Check lunch cost for a given day"""
        day_id = self.get_jour_id_par_date(date)
        return self._jours.avec_frais_repas_dejeuner_jour_par_date(day_id)

    def avec_frais_repas_gouter_jour_par_date(self, date: datetime.date) -> bool:
        """Check snack cost for a given day"""
        day_id = self.get_jour_id_par_date(date)
        return self._jours.avec_frais_repas_gouter_jour_par_date(day_id)

    def _check_input_data(self) -> None:
        """
        Check that:
        - total number of week(working and paid vacation) is less or equal to 52
        - total number of working week is less or equal to 47
        - total number of paid vacation week is less or equal to 5
        """

        working_week_count = self.get_semaines_travaillees_annee()
        paid_vacation_week_count = self.get_semaines_conges_payes_annee()

        if working_week_count + paid_vacation_week_count > 52:
            raise PlanningError(
                "Total number of week(working and paid vacation) is more than 52"
                f" ({working_week_count + paid_vacation_week_count}))")

        if working_week_count > 47:
            raise PlanningError(f"Total number of working week is more than 47 ({working_week_count})")

        if paid_vacation_week_count < 5:
            raise PlanningError(
                f"Total number of paid vacation week is less than 5 ({paid_vacation_week_count})")
