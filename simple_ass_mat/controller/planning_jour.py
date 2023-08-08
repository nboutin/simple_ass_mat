"""
:author Nicolas Boutin
:date 2023-08
"""
# pylint: disable=logging-fstring-interpolation

import datetime

from . import helper


class JourIdError(ValueError):
    """Jour Id error"""


class HorairesError(ValueError):
    """Horaires error"""


class PlanningJour:
    """Gère le planning de garde pour un jour
    jours:
        0:
            horaires: dict[str, str]
            dejeuner: bool
            gouter: bool
    """

    jour_id_t = int
    horaires_t = dict[str, str]
    jours_t = dict[jour_id_t, horaires_t]

    def __init__(self, jours_data: jours_t):
        self._jours = jours_data

    def get_heures_travaillees_par_jour_id(self, jour_id: jour_id_t) -> float:
        """Calcul le nombre d'heures travaillées pour un jour donné par jour_id"""
        horaires = self._get_horaires_par_jour_id(jour_id)
        duree: datetime.timedelta = helper.convert_time_ranges_to_duration(horaires)
        heures_travaillees: float = duree.seconds / 3600.0
        return heures_travaillees

    def avec_frais_repas_dejeuner_jour_par_date(self, jour_id: jour_id_t) -> bool:
        """Verifie si le dejeuner est compris pour un jour donné par jour_id"""
        try:
            jour = self._get_jour(jour_id)
        except JourIdError:
            return False

        try:
            return jour['dejeuner']
        except KeyError:
            return False

    def avec_frais_repas_gouter_jour_par_date(self, jour_id: jour_id_t) -> bool:
        """Verifie si le gouter est compris pour un jour donné par jour_id"""
        try:
            jour = self._get_jour(jour_id)
        except JourIdError:
            return False

        try:
            return jour['gouter']
        except KeyError:
            return False

    def _get_jour(self, jour_id: jour_id_t) -> dict:
        """Retourne un jour par id"""
        try:
            jour = self._jours[jour_id]
        except KeyError as key_error:
            raise JourIdError(f"jour_id {jour_id} not found") from key_error

        return jour

    def _get_horaires_par_jour_id(self, day_id: jour_id_t) -> horaires_t:
        """Retourne les horaires pour un jour donné par jour_id"""
        jour = self._get_jour(day_id)
        try:
            horaires = jour['horaires']
        except KeyError as key_error:
            raise HorairesError(f"horaires not found for {day_id}") from key_error

        return horaires
