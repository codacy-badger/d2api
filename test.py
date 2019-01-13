#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

import d2api
from d2api.src import endpoints
from d2api.src import entities
from d2api.src import errors as d2errors
from d2api.src import wrappers
from d2api import update_local_data


class APIPreliminaryTests(unittest.TestCase):
    def test_environment_api_key_set(self):
        self.assertIsNotNone(os.environ.get('D2_API_KEY'), 
        'D2_API_KEY was not set in environment')

    def test_correct_api_key(self):
        key = 'abcdxyz'
        tmp_api = d2api.APIWrapper(key)

        with self.assertRaises(d2errors.APIAuthenticationError, 
        msg = f'Request with API key \'{key}\' should raise authentication error'):
            tmp_api.get_match_details('4176987886')
    
    def test_insufficient_params(self):
        with self.assertRaises(d2errors.APIInsufficientArguments, msg = "match_id is a required argument for get_match_details"):
            d2api.APIWrapper().api_call(endpoints.GET_MATCH_DETAILS)

    def test_logger_check(self):
        tmp_api = d2api.APIWrapper(logging_enabled = True)
        self.assertIsNotNone(tmp_api.logger, 
        'Logger should not be None when \'logging_enabled\' was set to True')

    def test_update_local_files(self):
        self.assertNotEqual(update_local_data(), {},
        msg = "Update must return remote metadata. Instead, it returned an empty dict.")



class EndpointTests(unittest.TestCase):
    """
    Working endpoints cause 403(authentication) error.
    Enpoints that do not exist/are discontinued cause 404(not found) error.
    """
    def setUp(self):
        api = d2api.APIWrapper(api_key = "0000")
        self.api_call = api.api_call

    def test_get_match_history_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_HISTORY endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_HISTORY)
    
    def test_get_match_history_by_seq_num_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_HISTORY_BY_SEQ_NUM endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM)
    
    def test_get_match_details_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_DETAILS endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_DETAILS, match_id = '123')
    
    def test_get_heroes_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_HEROES endpoint is not working as intended."):
            self.api_call(endpoints.GET_HEROES)
    
    def test_get_game_items_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_GAME_ITEMS endpoint is not working as intended."):
            self.api_call(endpoints.GET_GAME_ITEMS)

class DtypeTests(unittest.TestCase):
    def test_steam_32_64(self):
        steam32 = 123456
        steam64 = 76561197960265728 + steam32
        account1 = entities.SteamAccount(account_id = steam64)
        account2 = entities.SteamAccount(account_id = steam32)
        self.assertEqual(account1, account2,
        'SteamAccount created with 32 Bit or 64 Bit SteamID should be indistinguishable')
    
    def test_basewrapper(self):
        test_obj = wrappers.BaseWrapper({'a':1, 'b':2, 'c':3})
        test_obj2 = wrappers.BaseWrapper({'a':1, 'b':2, 'c':3})
        self.assertEqual(test_obj.a, 1, 'BaseWrapper __getattr__ does not work as intended.')
        self.assertEqual(test_obj['b'], 2, 'BaseWrapper __getitem__ does not work as intended.')
        self.assertEqual(test_obj, test_obj2, 'BaseWrapper __eq__ does not work as intended.')
    


class MatchHistoryTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history = api.get_match_history
    
    def test_get_match_history_dtype(self):
        self.assertIsInstance(self.get_match_history(), wrappers.MatchHistory, 
        'get_match_history() should return a MatchHistory object')

# m = cur.get_match_details('4176987886')

# steamIDs = [114539087, 4294967295, 4294967295, 30633942, 78964422, 4294967295, 283619584, 20778465, 4294967295, 59769890]

class MatchDetailsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_details = api.get_match_details
    
    def test_get_match_details_dtype(self):
        match_id = '4176987886'
        self.assertIsInstance(self.get_match_details(match_id), wrappers.MatchDetails,
        f'get_match_details(\'{match_id}\') should return a MatchDetails object')

    def test_incorrect_matchid(self):
        res = self.get_match_details(match_id = 1)
        self.assertTrue(res.error, msg = 'Incorrect match_id should have response error')
    
    def test_match_content(self):
        match_id = '4176987886'
        res = self.get_match_details(match_id)

        q = res.players_minimal[0].hero
        a = entities.Hero(35)
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\').players_minimal[0].hero is {a}')

        q = res.players[6].items()[0].item_name
        a = 'item_tango'
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\').players[6].items()[0].item_name is {a}')

class HeroesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_heroes = api.get_heroes
    
    def test_get_heroes_dtype(self):
        self.assertIsInstance(self.get_heroes(), wrappers.Heroes,
        'get_heroes() should return a Heroes object')

    def test_hero_localized_name(self):
        res = self.get_heroes()
        cur_id = 59
        cur_hero = [h for h in res.heroes if h.id == cur_id][0]
        self.assertEqual(cur_hero.localized_name, 'Huskar',
        f'Localized name of id = {cur_id} should be Huskar')

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_game_items = api.get_game_items
    
    def test_get_game_items_dtype(self):
        self.assertIsInstance(self.get_game_items(), wrappers.GameItems,
        'get_game_items() should return a GameItems object')
        
    def test_item_localized_name(self):
        res = self.get_game_items()
        cur_id = 265
        cur_item = [i for i in res.items if i.id == cur_id][0]
        self.assertEqual(cur_item.localized_name, 'Infused Raindrops',
        f'Localized name of id = {cur_id} should be Infused Raindrops')

class TournamentPrizePoolTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_tournament_prize_pool = api.get_tournament_prize_pool
    
    def test_get_tournament_prize_pool_dtype(self):
        self.assertIsInstance(self.get_tournament_prize_pool(), wrappers.TournamentPrizePool,
        'get_tournament_prize_pool() shoult return a TournamentPrizePool object.')

if __name__ == '__main__':
    unittest.main()
