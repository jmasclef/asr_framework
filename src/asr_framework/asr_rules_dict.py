"""
    Copyright 2021 SEIDO CONSEILS S.A.S.
    This file is part of Framework Assistance Sémantique au Recrutement (ASR).

    Framework Assistance Sémantique au Recrutement (ASR) is free software:
    you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Framework Assistance Sémantique au Recrutement (ASR) is distributed
    in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Framework Assistance Sémantique au Recrutement (ASR).
    If not, see <https://www.gnu.org/licenses/>.
"""


import unittest

def asr_optimize_rules_dict(rules_dict:dict)->dict:
    """
    Retire les A->A et optimise en applicant la règle MAXIMUM de clés, MINIMUM de valeurs
    Qui autorise un maximum de vocabulaire à l'entrée pour un minimum de tokens
    Donc A->B, B->C, C->D devient A->D, B->D, C->D et non pas seulement A->D sinon les clés B et C sont perdues
    :param rules_dict: dict à otimiser
    :return: dict otimisé
    """
    futur_rules_dict=dict()
    for key, value in rules_dict.items():
        #on déroule les éventuelles poupées russes: A->B devient A->D
        try:
            final_value=asr_trackRuleTarget(rules_dict, value)
        except:
            #règle circulaire, on jette
            continue
        if key!=final_value:
            futur_rules_dict[key]=final_value
    return futur_rules_dict

def asr_apply_rules_dict(line_of_words_list:list[str],rules_dict:dict)->list[str]:
    """
    Remplace un mot par une alternative, le plus souvent une déclinaison du mot.
    Souvent le token remplacé est inconnu du modèle cible.
    Utilisé pour les déclinaisons de mots, grammaticales, orthographiques, mais aussi par détection des fautes d'accents courantes
    Les dynamic_rules sont construites automatiquement par itérations successives.
    Les static_rules sont des corrections optionnelles inscrites manuellement et en complément.
    Exemples:
    "electriques":"électrique"
    "emballeuse":"emballer"
    :param line_of_words_list: opération post-tokenisation, demande une liste de mots
    :param rules_dict: dictionnaire isolé et préalablement chargé directement du fichier open-data/dynamic_rules.csv
    :return: la chaîne aprèes remplacements, les token inconnus des dynamic_rules sont laissés inchangés
    """
    # if not rules_dict:
    #     func_name=__name__+'.'+'asr_apply_dynamic_rules'
    #     asr_logger.critical("{0} demande un dict() soit en rules_dict sinon intégré dans un asr_dictionary".format(func_name))
    #     raise 'Aucun dictionnaire de transmis.'

    return [rules_dict[word] if word in rules_dict else word for word in line_of_words_list]

def asr_merge_rules_dicts(most_reliable_rules_dict:dict, less_reliable_rules_dict:dict, split_targets=False)->dict:
    #On part du plus fiable qu'on va ensuite enrichir
    futur_rules_dict=asr_optimize_rules_dict(most_reliable_rules_dict)
    less_reliable_rules_dict= asr_optimize_rules_dict(less_reliable_rules_dict)
    # On reçoit une règle secondaire A->B,
    # On projette chaque membre dans les règles prioritaires
    # On vérifie que la réciproque n'est pas déja active
    # Si non, on crée une nouvelle règle

    #on scanne et on corrige les autres clés du dict le moins fiable
    for old_key, old_value in less_reliable_rules_dict.items():
        #si le dictionnaire de regles secondaires comprend des règles en poupées russes,
        # on dépile les règles pour garder la valeur finale
        old_key     =   asr_trackRuleTarget(futur_rules_dict,old_key)
        old_value   =   asr_trackRuleTarget(futur_rules_dict,old_value)
        if asr_trackRuleTarget(futur_rules_dict,old_value) != asr_trackRuleTarget(futur_rules_dict,old_key):
            futur_rules_dict[asr_trackRuleTarget(futur_rules_dict,old_key)] \
                = asr_trackRuleTarget(futur_rules_dict,old_value)

    return asr_optimize_rules_dict(futur_rules_dict)

def asr_trackRuleTarget(dict,word):
    #fonction récurrente qui retourne c si a->b->c
    try:
        if word not in dict.keys():
            return word
        else:
            if dict[word] in dict.keys():
                return asr_trackRuleTarget(dict,dict[word])
            else:
                return dict[word]
    except:
        raise NameError("Looping rule for {0}".format(word))


class test_asr_rules_dict_methods(unittest.TestCase):

    def setUp(self):
        self.a_dict = {'a': 'b', 'b': 'c', 'c': 'd', 'z' : 'z'}
        self.a_dict_optimized = {'a': 'd', 'b': 'd', 'c': 'd'}
        self.b_dict = {'a': 'b', 'b': 'c', 'c': 'd', 'd' : 'b'}
        self.b_dict_optimized = { } #règles circulaires
        self.c_dict = {'a': 'k', 'b': 'k', 'c': 'd', 'n' : 'e'}
        self.d_dict = {'k': 'l', 'b': 'm', 'c': 'n'}
        # Merge avec d prioritaire, calculs vérifiés
        # {'k': 'l', 'b': 'l', 'c': 'e', 'a': 'l', 'm': 'l', 'n': 'e', 'd': 'e'}
        # Merge avec c prioritaire, calculs vérifiés
        # {'a': 'm', 'b': 'm', 'c': 'e', 'n': 'e', 'k': 'm', 'l': 'm', 'd': 'e'}

    def test_asr_rules_dict(self):
        self.assertEqual(asr_optimize_rules_dict(self.a_dict),self.a_dict_optimized)
        self.assertEqual(asr_optimize_rules_dict(self.b_dict),self.b_dict_optimized)
        self.assertEqual(asr_merge_rules_dicts(most_reliable_rules_dict=self.d_dict,less_reliable_rules_dict=self.c_dict),
                         {'k': 'l', 'b': 'l', 'c': 'e', 'a': 'l', 'm': 'l', 'n': 'e', 'd': 'e'})
        self.assertEqual(asr_merge_rules_dicts(most_reliable_rules_dict=self.c_dict,less_reliable_rules_dict=self.d_dict),
                         {'a': 'm', 'b': 'm', 'c': 'e', 'n': 'e', 'k': 'm', 'l': 'm', 'd': 'e'})



if __name__ == '__main__':
    unittest.main()
