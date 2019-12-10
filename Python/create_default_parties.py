#!/usr/bin/env python
from InvokePSQL import InvokePSQL
from Party import Party


def gen_party(character_id_str, party_composition_id, name, ability_array_str, level, gender_candidate):
    db = InvokePSQL()
    Party(db=db,
          character_id_str=character_id_str,
          party_composition_id=party_composition_id,
          name=name,
          ability_array_str=ability_array_str,
          level=level,
          gender_candidate=gender_candidate)


if __name__ == '__main__':
    gen_party(None, 1, 'AllStars_3', '18,18,18,18,18,18', 1, 'Random')
    gen_party(None, 11, 'AllStars_4', '18,18,18,18,18,18', 1, 'Random')
    gen_party(None, 21, 'AllStars_5', '18,18,18,18,18,18', 1, 'Random')
    gen_party(None, 31, 'AllStars_6', '18,18,18,18,18,18', 1, 'Random')

    gen_party(None, 1, 'AvgJoes_3', '10,10,10,10,10,10', 1, 'Random')
    gen_party(None, 11, 'AvgJoes_4', '10,10,10,10,10,10', 1, 'Random')
    gen_party(None, 21, 'AvgJoes_5', '10,10,10,10,10,10', 1, 'Random')
    gen_party(None, 31, 'AvgJoes_6', '10,10,10,10,10,10', 1, 'Random')

    gen_party(None, 1, 'Low_3', '6,6,6,6,6,6', 1, 'Random')
    gen_party(None, 11, 'Low_4', '6,6,6,6,6,6', 1, 'Random')
    gen_party(None, 21, 'Low_5', '6,6,6,6,6,6', 1, 'Random')
    gen_party(None, 31, 'Low_6', '6,6,6,6,6,6', 1, 'Random')

    gen_party(None, 1, 'common_3', 'Common', 1, 'Random')
    gen_party(None, 11, 'common_4', 'Common', 1, 'Random')
    gen_party(None, 21, 'common_5', 'Common', 1, 'Random')
    gen_party(None, 31, 'common_6', 'Common', 1, 'Random')

    gen_party(None, 1, 'strict_3', 'Strict', 1, 'Random')
    gen_party(None, 11, 'strict_4', 'Strict', 1, 'Random')
    gen_party(None, 21, 'strict_5', 'Strict', 1, 'Random')
    gen_party(None, 31, 'strict_6', 'Strict', 1, 'Random')

    gen_party(None, 1, 'standard_3', 'standard', 1, 'Random')
    gen_party(None, 11, 'standard_4', 'standard', 1, 'Random')
    gen_party(None, 21, 'standard_5', 'standard', 1, 'Random')
    gen_party(None, 31, 'standard_6', 'standard', 1, 'Random')

    gen_party(None, 1, 'point_buy_even_3', 'point_buy_even', 1, 'Random')
    gen_party(None, 11, 'point_buy_even_4', 'point_buy_even', 1, 'Random')
    gen_party(None, 21, 'point_buy_even_5', 'point_buy_even', 1, 'Random')
    gen_party(None, 31, 'point_buy_even_6', 'point_buy_even', 1, 'Random')

    gen_party(None, 1, 'point_buy_one_max_3', 'point_buy_one_max', 1, 'Random')
    gen_party(None, 11, 'point_buy_one_max_4', 'point_buy_one_max', 1, 'Random')
    gen_party(None, 21, 'point_buy_one_max_5', 'point_buy_one_max', 1, 'Random')
    gen_party(None, 31, 'point_buy_one_max_6', 'point_buy_one_max', 1, 'Random')

    gen_party(None, 1, 'point_buy_two_max_3', 'point_buy_two_max', 1, 'Random')
    gen_party(None, 11, 'point_buy_two_max_4', 'point_buy_two_max', 1, 'Random')
    gen_party(None, 21, 'point_buy_two_max_5', 'point_buy_two_max', 1, 'Random')
    gen_party(None, 31, 'point_buy_two_max_6', 'point_buy_two_max', 1, 'Random')

    gen_party(None, 1, 'point_buy_three_max_3', 'point_buy_three_max', 1, 'Random')
    gen_party(None, 11, 'point_buy_three_max_4', 'point_buy_three_max', 1, 'Random')
    gen_party(None, 21, 'point_buy_three_max_5', 'point_buy_three_max', 1, 'Random')
    gen_party(None, 31, 'point_buy_three_max_6', 'point_buy_three_max', 1, 'Random')
