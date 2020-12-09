# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, TypedDict

import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests

from .data.heroes import heroes_by_id, heroes_by_name
from .data.items import items_by_id


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
        hero_name: str = hero_slot_value if not isinstance(
            hero_slot_value, list) else hero_slot_value[0]

        hero = heroes_by_name[hero_name]
        hero_id = hero['id']

        res = requests.get(
            f'https://api.opendota.com/api/heroes/{ str(hero_id) }/itemPopularity')

        data: ItemPopularity = res.json()
        data_pd = pd.DataFrame(data).fillna(0)

        start_items = data_pd['start_game_items'].nlargest(8).transpose()
        early_items = data_pd['early_game_items'].nlargest(8).transpose()
        mid_items = data_pd['mid_game_items'].nlargest(8).transpose()
        late_items = data_pd['late_game_items'].nlargest(8).transpose()

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
