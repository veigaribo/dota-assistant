from typing import cast, Dict, List, TypedDict

import requests


class Item(TypedDict):
    id: int
    hint: List[str]
    img: str
    dname: str
    qual: str
    cost: int
    notes: str


class NamedItem(Item):
    name: str


items_content = requests.get('https://api.opendota.com/api/constants/items')
items: Dict[str, Item] = items_content.json()

items_by_name: Dict[str, NamedItem] = {
    item['dname']: cast(NamedItem, {
        **item,
        'name': name
    })
    for name, item in items.items()
    if 'dname' in item
}

items_by_id: Dict[int, NamedItem] = {
    item['id']: cast(NamedItem, {
        **item,
        'name': name
    })
    for name, item in items.items()
}
