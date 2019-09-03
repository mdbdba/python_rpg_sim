#!/usr/bin/env python
import click
from InvokePSQL import InvokePSQL
from Party import Party

@click.command()
@click.option('-c','--character_id_str', default=None, help='Use if you already have characters and just want them in a party.')
@click.option('-p','--party_composition_id', default='11', show_default=True, help='Defines the classes in the party')
@click.option('-n','--name', required=True, help='Identifier for the party')
@click.option('-a', '--ability_array_str', default='Common', show_default=True,
              help='The ability values for each of the characters in the party')
@click.option('-l', '--level', default=1, show_default=True, help='The character level for the party')
@click.option('-g', '--gender_candidate', default='Random', show_default=True, help='The character gender')

def gen_party(character_id_str, party_composition_id, name, ability_array_str, level, gender_candidate):
    db = InvokePSQL()
    a1 = Party(db=db,
               character_id_str=character_id_str,
               party_composition_id=party_composition_id,
               name=name,
               ability_array_str=ability_array_str,
               level=level,
               gender_candidate=gender_candidate)

if __name__ == '__main__':
    gen_party()
