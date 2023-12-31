"""
:date 2023-08-07
:author Nicolas Boutin
"""

# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=protected-access

import unittest
import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))  # OK


from simple_ass_mat.controller.planning.planning import Planning  # nopep8 # noqa: E402
from simple_ass_mat.controller.planning.planning_jour import PlanningJour  # nopep8 # noqa: E402
from simple_ass_mat.controller.planning.planning_semaine import PlanningSemaine  # nopep8 # noqa: E402
from simple_ass_mat.controller.planning.planning_annee import PlanningAnnee  # nopep8 # noqa: E402


class TestGetJourIdParDate(unittest.TestCase):

    def test_nominal(self):

        annee = {
            0: [[1, 5], [8, 14], [17, 27], [36, 42], [45, 51]],
            1: [[7], [16], [28], [34, 35], [44]]}

        semaines = {0: {"lundi": None, "mardi": None,
                        "mercredi": 1,
                        "jeudi": None,
                        "vendredi": None,
                        "samedi": None,
                        "dimanche": None},
                    1: {"lundi": None,
                        "mardi": 0,
                        "mercredi": 1,
                        "jeudi": 0,
                        "vendredi": 0,
                        "samedi": None,
                        "dimanche": None}}
        planning_jour = PlanningJour({})
        planning_semaine = PlanningSemaine(semaines, planning_jour)
        planning_annee = PlanningAnnee(annee)
        planning = Planning(planning_jour, planning_semaine, planning_annee, [[1, 5]])

        self.assertEqual(planning._get_jour_id_par_date(date(2023, 1, 30)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 1, 31)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 1)), 1)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 2)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 3)), None)

        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 6)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 7)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 8)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 9)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 10)), None)

        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 13)), None)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 14)), 0)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 15)), 1)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 16)), 0)
        self.assertEqual(planning._get_jour_id_par_date(date(2023, 2, 17)), 0)


if __name__ == '__main__':
    import locale
    locale.setlocale(locale.LC_ALL, 'fr-FR')

    import logging
    from pathlib import Path

    logging.basicConfig(level=logging.DEBUG, handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / Path(__file__ + '.log'), mode='w')])

    unittest.main()
