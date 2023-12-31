"""
:date 2023-07-12
:author Nicolas Boutin
:brief https://devenirassmat.com/la-mensualisation-cest-obligatoire/
"""

# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

import unittest
import sys
import os
from pathlib import Path
from datetime import date

import yaml


sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))  # OK


from simple_ass_mat.controller import factory  # nopep8 # noqa: E402
from simple_ass_mat.controller.pajemploi_declaration import PajemploiDeclaration  # nopep8 # noqa: E402


class TestDevenirAssmatAnneeComplete(unittest.TestCase):
    """Test Devenir AssMat"""

    def setUp(self):
        data_filepath = Path(__file__).parent / "data_devenir_assmat_annee_complete_4.yml"
        with open(data_filepath, 'r', encoding='UTF-8') as file:
            data = yaml.safe_load(file)
        self.contrat = factory.make_contrat(data['contrat'])
        self.planning = self.contrat.planning
        self.garde = self.contrat.garde

        self.pajemploi_declaration = PajemploiDeclaration(self.contrat)

    @unittest.skip("Use case not handle")
    def test_calcul_annee_complete(self):
        """52 semaines, année complète
        47 semaines travaillées
        50h/sem, 5j/sem, 10h/j
        Salaire horaire net 3€
        Salaire horaire net majoree 4€
        Salaire net mensualisé 650€
        --
        2020-02 4 semaines completes = 4 * 5h majorees + 20€
        2020-05 5 semaines completes = 5 * 5h majorees + 25€
        """
        self.assertTrue(self.planning.is_annee_complete())
        self.assertEqual(self.planning.get_jours_travailles_semaine_par_id(0), 5)
        self.assertEqual(self.planning.get_heures_travaillees_semaine_par_id(0), 50)
        self.assertEqual(self.contrat.get_salaire_net_mensualise(), 650)

        mois_courant = date(2020, 2, 1)
        week_number = 6

        self.assertEqual(self.garde.get_heures_complementaires_semaine_par_date(mois_courant.year, week_number), 0)
        self.assertEqual(self.garde.get_heures_complementaires_mois_par_date(mois_courant), 0)
        self.assertEqual(self.garde.get_heures_majorees_semaine_par_date(mois_courant.year, week_number), 5)
        self.assertEqual(self.garde.get_heures_majorees_mois_par_date(mois_courant), 20)
        self.assertEqual(self.contrat.get_salaire_net_mois_par_date(mois_courant), 475.10)


if __name__ == '__main__':
    import locale
    locale.setlocale(locale.LC_ALL, 'fr-FR')

    unittest.main()
