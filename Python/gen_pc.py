#!/usr/bin/env python
import click
from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter

@click.command()
@click.option('--race_candidate', default='Wood elf', help='Character Race')
@click.option('--class_candidate', default='Ranger', help='Character Class')
@click.option('--ability_array_str', default='10,10,10,10,10,10',
              help='The ability values for the character in order')
@click.option('--level', default=1, help='The character level')
@click.option('--gender_candidate', default='M', help='The character gender')
def gen_pc(race_candidate, class_candidate, ability_array_str, level, gender_candidate):
    print(f'Creating a {gender_candidate} level {level} {race_candidate} {class_candidate} with abilities: {ability_array_str}')
    db = InvokePSQL()
    print("Debug info follows")
    a1 = PlayerCharacter(db=db, debug_ind=1, class_candidate=class_candidate,
                         race_candidate=race_candidate, ability_array_str=ability_array_str,
                         level=level, gender_candidate=gender_candidate)
    print("ClassEval info follows")
    for i in range(len(a1.get_class_eval())):
        for key, value in a1.get_class_eval()[i].items():
            print(f"{i} -- {str(key).ljust(25)}: {value}")

if __name__ == '__main__':
    gen_pc()
