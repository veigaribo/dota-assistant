from typing import Any, Dict, List, Text, TypedDict, Union

import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests

from .data.heroes import heroes_by_name
from .data.items import items_by_id
from .utils import first_item_or_id


class ItemPopularity(TypedDict):
    start_game_items: Dict[str, int]
    early_game_items: Dict[str, int]
    mid_game_items: Dict[str, int]
    late_game_items: Dict[str, int]


class ActionListItems(Action):
    def name(self) -> Text:
        return "action_list_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hero_slot_value: Union[str, List[str]] = tracker.get_slot('hero')

        # if its a list, use the first element
        hero_name: str = first_item_or_id(hero_slot_value)

        hero = heroes_by_name[hero_name]
        hero_id = hero['id']

        res = requests.get(
            f'https://api.opendota.com/api/heroes/{ str(hero_id) }/itemPopularity')

        data: ItemPopularity = res.json()
        data_pd = pd.DataFrame(data).fillna(0)

        def get_largest(series):
            with_zeroes = series.nlargest(8)
            return with_zeroes[with_zeroes != 0.0].transpose()

        start_items = get_largest(data_pd['start_game_items'])
        early_items = get_largest(data_pd['early_game_items'])
        mid_items = get_largest(data_pd['mid_game_items'])
        late_items = get_largest(data_pd['late_game_items'])

        message = '\n'.join([
            f'itens iniciais:\n\n{ ActionListItems.format_items(start_items) }',
            f'early jogo:\n\n{ ActionListItems.format_items(early_items) }',
            f'mid jogo:\n\n{ ActionListItems.format_items(mid_items) }',
            f'late jogo:\n\n{ ActionListItems.format_items(late_items) }',
        ])

        dispatcher.utter_message(text=message)

        return [SlotSet('hero', None)]

    @staticmethod
    def format_items(items):
        return '\n'.join([f'- { items_by_id[int(item_id)].get("dname") } (usado { str(quantity) } vezes)'
                          for item_id, quantity in items.items()])
