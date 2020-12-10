from typing import List, TypedDict


class Lane(TypedDict):
    id: int
    name: str
    dname: str


lanes: List[Lane] = [
    {'id': 1, 'name': 'safe', 'dname': 'Safe'},
    {'id': 2, 'name': 'mid', 'dname': 'Mid'},
    {'id': 3, 'name': 'off', 'dname': 'Off'},
    {'id': 4, 'name': 'jungle', 'dname': 'Mato'}
]

lanes_by_name = {
    lane['name']: lane
    for lane in lanes
}

lanes_by_id = {
    lane['id']: lane
    for lane in lanes
}
