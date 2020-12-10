from typing import Any, Dict, List, Optional, Text, TypedDict, Union

import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import requests

from .data.heroes import Hero, heroes_by_name, heroes_by_id
from .data.lanes import Lane, lanes_by_name, lanes_by_id
from .utils import first_item_or_id


class LaneRole(TypedDict):
    hero_id: int
    lane_role: int
    time: int
    games: str
    wins: str


class ValidateLanesForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_lanes_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[Text]]:
        # if there is a lane, we use that
        if tracker.get_slot('lane'):
            return []

        # if a lane was not provided, we ask for a hero
        return ['hero']


class ActionListLanes(Action):
    def name(self) -> Text:
        return "action_list_lanes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # by hero
        hero_slot_value: Union[str, List[str]] = tracker.get_slot('hero')

        if hero_slot_value:
            hero_name: str = first_item_or_id(hero_slot_value)
            hero = heroes_by_name[hero_name]

            return self.run_by_hero(dispatcher, tracker, domain, hero)

        # by lane
        lane_slot_value: Union[str, List[str]] = tracker.get_slot('lane')

        lane_name: str = first_item_or_id(lane_slot_value)
        lane = lanes_by_name[lane_name]

        return self.run_by_lane(dispatcher, tracker, domain, lane)

    def run_by_hero(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any],
                    hero: Hero) -> List[Dict[Text, Any]]:

        res = requests.get(
            f'https://api.opendota.com/api/scenarios/laneRoles', params={'hero_id': hero['id']})

        data: List[LaneRole] = res.json()
        data_pd = pd.DataFrame(data).astype(
            {'games': 'int64', 'wins': 'int64'})

        times_collapsed = data_pd.groupby(
            ['hero_id', 'lane_role']).sum().sort_values('games', ascending=False).reset_index()

        message = ActionListLanes.format_lanes_by_hero(
            times_collapsed.transpose())

        dispatcher.utter_message(text=message)

        return [SlotSet('hero', None), SlotSet('lane', None)]

    def run_by_lane(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any],
                    lane: Lane) -> List[Dict[Text, Any]]:

        res = requests.get(
            f'https://api.opendota.com/api/scenarios/laneRoles', params={'lane_role': lane['id']})

        data: List[LaneRole] = res.json()
        data_pd = pd.DataFrame(data).astype(
            {'games': 'int64', 'wins': 'int64'})

        times_collapsed = data_pd.groupby(
            ['hero_id', 'lane_role']).sum()

        top_heroes = times_collapsed.nlargest(10, 'games').reset_index()

        message = ActionListLanes.format_lanes_by_lane(
            top_heroes.transpose())

        dispatcher.utter_message(text=message)

        return [SlotSet('hero', None), SlotSet('lane', None)]

    @staticmethod
    def format_lanes_by_hero(lanes_roles):
        hero_id = lanes_roles[0]['hero_id']
        hero = heroes_by_id[hero_id]

        return f'lanes para { hero["localized_name"] }\n' + '\n'.join([ActionListLanes.format_lane_by_hero(i, lane_role) for i, lane_role in lanes_roles.items()])

    @staticmethod
    def format_lane_by_hero(i: int, lane_role):
        lane_id = lane_role['lane_role']
        lane = lanes_by_id[lane_id]
        lane_name = lane['dname']
        games = lane_role['games']
        wins = lane_role['wins']

        return f'{ str(i + 1) }. { lane_name }. games: { str(games) }, wins: { str(wins) }' + \
            (f' ({ wins * 100 / games }%)' if games > 0 else '')

    @staticmethod
    def format_lanes_by_lane(lanes_roles):
        lane_id = lanes_roles[0]['lane_role']
        lane = lanes_by_id[lane_id]

        return f'herois para lane { lane["dname"] }\n' + '\n'.join([ActionListLanes.format_lane_by_lane(i, lane_role) for i, lane_role in lanes_roles.items()])

    @staticmethod
    def format_lane_by_lane(i: int, lane_role):
        hero_id = lane_role['hero_id']
        hero = heroes_by_id[hero_id]
        hero_name = hero['localized_name']
        games = lane_role['games']
        wins = lane_role['wins']

        return f'{ str(i + 1) }. { hero_name }. games: { str(games) }, wins: { str(wins) }' + \
            (f' ({ wins * 100 / games }%)' if games > 0 else '')
