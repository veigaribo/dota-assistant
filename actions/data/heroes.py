from typing import Dict, List, TypedDict

import requests


class Hero(TypedDict):
    id: int
    name: str
    localized_name: str
    primary_attr: str
    attack_type: str
    roles: List[str]
    legs: int


heroes_content = requests.get('https://api.opendota.com/api/constants/heroes')
heroes: Dict[int, Hero] = heroes_content.json()

# slicing at 14 to strip the "npc_dota_hero_"
heroes_by_name = {
    hero['name'][14:].replace('_', ''): hero
    for _, hero in heroes.items()
}

heroes_by_id = {
    hero['id']: hero
    for _, hero in heroes.items()
}
