"""
:author Nicolas Boutin
:date 2023-07-04
"""
# pylint: disable=logging-fstring-interpolation

import logging
import datetime
from typing import NamedTuple

import controller.helper as helper
from controller.planning import Planning
from controller.garde import Garde

logger = logging.getLogger(__name__)


class Contrat:
    """Assistante maternelle contrat"""

    class SalairesHoraires(NamedTuple):
        """Salaires namedtuple"""
        horaire_net: float
        horaire_complementaires_net: float
        horaire_majorees_net: float

    def __init__(self, planning: Planning, salaires: SalairesHoraires, garde: Garde) -> None:
        self._planning = planning
        self._salaires = salaires
        self._garde = garde

    @property
    def planning(self) -> Planning:
        """Planning getter"""
        return self._planning

    @property
    def garde(self) -> Garde:
        """Garde getter"""
        return self._garde

    @property
    def salaires_horaires(self) -> SalairesHoraires:
        """SalairesHoraires getter"""
        return self._salaires

    def get_salaire_net_mensualise(self):
        """working_hour_per_month_count * net_hourly_rate"""
        return self._planning.get_heures_travaillees_mois_mensualisees() * self._salaires.horaire_net

    def get_salaire_net_mois_par_date(self, date: datetime.date) -> float:
        """Salaire net mensuel incluant heure complementaire et heure majoree"""
        salaire_net_mensualise = self.get_salaire_net_mensualise()
        heure_absence_non_remuneree = self._garde.get_heure_absence_non_remuneree_mois(date)
        heure_travaille_prevu = self._planning.get_heures_travaillees_prevu_mois_par_date(date)

        return salaire_net_mensualise \
            - (salaire_net_mensualise * heure_absence_non_remuneree / heure_travaille_prevu) \
            + self._garde.get_heures_complementaires_mois_par_date(date) * self._salaires.horaire_complementaires_net \
            + self._garde.get_heures_majorees_mois_par_date(date) * self._salaires.horaire_majorees_net

    def get_frais_entretien_mois_par_date(self, date: datetime.date) -> float:
        """Frais d'entretien mensuel"""
        dates = helper.get_dates_in_month(date)
        frais_entretien_mois = 0.0
        # acceuil_duree_seuil = 6.46  # round(6 + 28/60, 2)

        for i_date in dates:
            h_trav = self._garde.get_heures_travaillees_jour_par_date(i_date)
            if h_trav > 0:
                # frais_entretien_jour = max(2.65, round(h_trav * 2.65 / acceuil_duree_seuil, 2))
                frais_entretien_jour = self.get_frais_entretien_jour(h_trav, i_date)
                logger.debug(f"get_frais_entretien_mois_par_date: {i_date} {h_trav} {frais_entretien_jour}")
                frais_entretien_mois += frais_entretien_jour
        return frais_entretien_mois

    def get_frais_entretien_jour(self, duree: float, date: datetime.date) -> float:
        """Frais d'entretien journalier"""
        class FraisEntretien(NamedTuple):
            """FraisEntretien namedtuple"""
            minimum: float
            taux_9h: float

        frais_entretien_annuel = {2022: FraisEntretien(2.65, 3.39/9), 2023: FraisEntretien(2.65, 3.61/9)}
        frais_entretien = frais_entretien_annuel[date.year]
        value = 0.0

        if duree == 0:
            return value
        elif duree <= 9.0:
            value = max(duree * frais_entretien.taux_9h, frais_entretien.minimum)
        else:
            value = 9 * frais_entretien.taux_9h + (duree - 9) * frais_entretien.taux_9h
        return round(value, 2)
