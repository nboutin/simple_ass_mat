"""
Author: Nicolas Boutin
Date: 2023-08
Description:
"""


class Remuneration:
    """Handle ass mat remuneration"""

    def __init__(self, tarif_horaire_brut: float) -> None:
        self._tarif_horaire_brut = tarif_horaire_brut