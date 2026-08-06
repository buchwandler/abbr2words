"""Semantically equivalent dinner scenarios for every bundled language."""

from __future__ import annotations

from typing import Final

GERMAN_TEXT: Final = (
    "Zum 14.05.2026 um 18:20 Uhr ist das Abendessen geplant. "
    "Für den Auflauf brauchen wir 1,5 kg Kartoffeln, 500 g Quark, "
    "2 Eier, 1 l Milch und ggf. 3 cm mehr Backpapier. "
    "Prof. Klein sagt: „Bitte stelle die Form auf die 2. Schiene, "
    "backe alles für 45 Min. und lass es danach 1 Min. oder auch "
    "2 Min. ruhen.“ Die Kosten liegen bei ca. 12,80 EUR zzgl. Pfand."
)

ENGLISH_TEXT: Final = (
    "Dinner is planned for 05/14/2026 at 18:20. "
    "For the casserole, we need 1.5 kg potatoes, 500 g quark, "
    "2 eggs, 1 L milk and, if necessary, 3 cm more parchment paper. "
    "Prof. Klein says: “Please place the dish on the 2nd rack, "
    "bake everything for 45 min. and then let it rest for 1 min. or even "
    "2 min. before serving.” The cost is approx. 12.80 EUR plus a deposit."
)

CZECH_TEXT: Final = (
    "Večeře je naplánována na 14.05.2026 v 18:20. "
    "Na nákyp potřebujeme 1,5 kg brambor, 500 g tvarohu, "
    "2 vejce, 1 l mléka a v případě potřeby o 3 cm více pečicího papíru. "
    "Prof. Klein říká: „Položte formu na druhou mřížku, "
    "pečte vše 45 min. a potom nechte pokrm odpočívat 1 min. nebo i "
    "2 min. před podáváním.“ Cena je přibližně 12,80 EUR plus záloha."
)

SPANISH_TEXT: Final = (
    "La cena está prevista para el 14.05.2026 a las 18:20. "
    "Para el gratinado necesitamos 1,5 kg de patatas, 500 g de requesón, "
    "2 huevos, 1 l de leche y, si hace falta, 3 cm más de papel de horno. "
    "El Prof. Klein dice: «Coloque la fuente en la 2ª guía, "
    "hornee todo durante 45 min. y después déjelo reposar 1 min. o incluso "
    "2 min. antes de servirlo». El coste es de aprox. 12,80 EUR más el depósito."
)

FRENCH_TEXT: Final = (
    "Le dîner est prévu le 14.05.2026 à 18:20. "
    "Pour le gratin, il nous faut 1,5 kg de pommes de terre, 500 g de fromage blanc, "
    "2 œufs, 1 l de lait et, si nécessaire, 3 cm de papier cuisson en plus. "
    "Le Pr Klein dit : « Placez le plat sur le deuxième niveau, "
    "faites cuire le tout pendant 45 min puis laissez-le reposer 1 min ou même "
    "2 min avant de servir. » Le coût est d’env. 12,80 EUR, consigne en plus."
)

ITALIAN_TEXT: Final = (
    "La cena è prevista per il 14.05.2026 alle 18:20. "
    "Per lo sformato servono 1,5 kg di patate, 500 g di quark, "
    "2 uova, 1 l di latte e, se necessario, 3 cm di carta da forno in più. "
    "Il Prof. Klein dice: «Mettete la teglia sul secondo ripiano, "
    "cuocete tutto per 45 min. e poi lasciatelo riposare per 1 min. o anche "
    "2 min. prima di servirlo». Il costo è di ca. 12,80 EUR più il deposito."
)

PORTUGUESE_TEXT: Final = (
    "O jantar está marcado para 14.05.2026 às 18:20. "
    "Para o gratinado, precisamos de 1,5 kg de batatas, 500 g de quark, "
    "2 ovos, 1 l de leite e, se necessário, mais 3 cm de papel vegetal. "
    "O Prof. Klein diz: «Coloque a forma na segunda grelha, "
    "asse tudo durante 45 min. e depois deixe repousar 1 min. ou até "
    "2 min. antes de servir». O custo é de aprox. 12,80 EUR mais o depósito."
)

SAMPLES: Final[dict[str, tuple[str, str]]] = {
    "german": ("de", GERMAN_TEXT),
    "english": ("en-us", ENGLISH_TEXT),
    "czech": ("cs", CZECH_TEXT),
    "spanish": ("es", SPANISH_TEXT),
    "french": ("fr", FRENCH_TEXT),
    "italian": ("it", ITALIAN_TEXT),
    "portuguese": ("pt", PORTUGUESE_TEXT),
}
