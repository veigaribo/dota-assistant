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

from .data.config import SIGNIFICATIVE_MATCHUP_MIN_MATCHES
from .data.heroes import heroes_by_id, heroes_by_name


class Matchup(TypedDict):
    hero_id: int
    games_played: int
    wins: int


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

        message = f'tu pode pegar:\n\n{ActionListMatchups.format_matchups(top_win_percentages_transposed)}'

        dispatcher.utter_message(text=message)

        return [SlotSet('hero', None)]

    @staticmethod
    def format_matchups(matchups_with_win_percentages):
        return '\n'.join([ActionListMatchups.format_matchup(i, matchups_with_win_percentages[i])
                          for i in range(len(matchups_with_win_percentages))])

    @staticmethod
    def format_matchup(i: int, matchup_with_win_percentage):
        hero_name = heroes_by_id[matchup_with_win_percentage['hero_id']
                                 ]['localized_name']

        win_rate = matchup_with_win_percentage['win_percentage']
        wins = matchup_with_win_percentage['wins']
        games_played = matchup_with_win_percentage['games_played']

        return f'{ str(i + 1) } - { hero_name }: { str(win_rate * 100) }% win rate ({ str(games_played) } partidas, { str(wins) } vitórias)'
