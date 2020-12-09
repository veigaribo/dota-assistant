# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import json
from typing import Any, Text, Dict, List, Union

import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests

from .data.config import SIGNIFICATIVE_MATCHUP_MIN_MATCHES
from .data.heroes import Hero
from .data.matchups import Matchup

with open('./actions/data/heroes.json') as heroes_file:
    heroes_content = heroes_file.read()
    heroes: List[Hero] = json.loads(heroes_content)

# slicing at 14 to strip the "npc_dota_hero_"
heroes_by_name = {hero['name'][14:].replace('_', ''): hero for hero in heroes}
heroes_by_id = {hero['id']: hero for hero in heroes}


class ActionListMatchups(Action):

    def name(self) -> Text:
        return "action_list_matchups"

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
            f'https://api.opendota.com/api/heroes/{ str(hero_id) }/matchups')

        data: List[Matchup] = res.json()
        data_pd = pd.DataFrame(data)

        significant_matchups = data_pd[data_pd['games_played']
                                       >= SIGNIFICATIVE_MATCHUP_MIN_MATCHES]

        win_percentages = significant_matchups.assign(
            win_percentage=(1.0 - significant_matchups['wins'] / significant_matchups['games_played']))

        top_win_percentages = win_percentages.nlargest(
            5, 'win_percentage').reset_index()

        top_win_percentages_transposed = top_win_percentages.transpose()

        message = 'tu pode pegar:\n\n' + \
            '\n'.join([ActionListMatchups.format_win_percentage(i, top_win_percentages_transposed[i])
                       for i in range(len(top_win_percentages))])

        dispatcher.utter_message(text=message)

        return [SlotSet('hero', None)]

    @staticmethod
    def format_win_percentage(i: int, win_percentage):
        hero_name = heroes_by_id[win_percentage['hero_id']]['localized_name']
        win_rate = win_percentage['win_percentage']
        wins = win_percentage['wins']
        games_played = win_percentage['games_played']

        return f'{ str(i + 1) } - { hero_name }: { str(win_rate * 100) }% win rate ({ str(games_played) } partidas, { str(wins) } vitórias)'
