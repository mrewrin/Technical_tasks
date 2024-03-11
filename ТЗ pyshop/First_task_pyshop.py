from pprint import pprint
import random
import math
import unittest

TIMESTAMPS_COUNT = 50000

PROBABILITY_SCORE_CHANGED = 0.0001

PROBABILITY_HOME_SCORE = 0.45

OFFSET_MAX_STEP = 3

INITIAL_STAMP = {
    "offset": 0,
    "score": {
        "home": 0,
        "away": 0
    }
}


def generate_stamp(previous_value):
    score_changed = random.random() > 1 - PROBABILITY_SCORE_CHANGED
    home_score_change = 1 if score_changed and random.random() > 1 - \
        PROBABILITY_HOME_SCORE else 0
    away_score_change = 1 if score_changed and not home_score_change else 0
    offset_change = math.floor(random.random() * OFFSET_MAX_STEP) + 1

    return {
        "offset": previous_value["offset"] + offset_change,
        "score": {
            "home": previous_value["score"]["home"] + home_score_change,
            "away": previous_value["score"]["away"] + away_score_change
        }
    }


def generate_game():
    stamps = [INITIAL_STAMP, ]
    current_stamp = INITIAL_STAMP
    for _ in range(TIMESTAMPS_COUNT):
        current_stamp = generate_stamp(current_stamp)
        stamps.append(current_stamp)

    return stamps


game_stamps = generate_game()

pprint(game_stamps)


def get_score(game_stamps, offset):
    if not game_stamps or offset < game_stamps[0]["offset"]:
        return INITIAL_STAMP["score"]["home"], INITIAL_STAMP["score"]["away"]

    home_score, away_score = INITIAL_STAMP["score"]["home"], INITIAL_STAMP["score"]["away"]

    left, right = 0, len(game_stamps) - 1
    while left <= right:
        mid = (left + right) // 2
        if game_stamps[mid]["offset"] <= offset:
            home_score, away_score = game_stamps[mid]["score"]["home"], game_stamps[mid]["score"]["away"]
            left = mid + 1
        else:
            right = mid - 1

    return home_score, away_score


class TestGetScore(unittest.TestCase):
    def setUp(self):
        self.game_stamps = generate_game()

    def test_empty_game_stamps(self):
        self.assertEqual(get_score([], 100), (INITIAL_STAMP["score"]["home"], INITIAL_STAMP["score"]["away"]))

    def test_offset_less_than_first_stamp(self):
        self.assertEqual(get_score(self.game_stamps, -1),
                         (INITIAL_STAMP["score"]["home"], INITIAL_STAMP["score"]["away"]))

    def test_offset_greater_than_last_stamp(self):
        last_stamp = self.game_stamps[-1]
        expected_score = last_stamp["score"]["home"], last_stamp["score"]["away"]
        self.assertEqual(get_score(self.game_stamps, last_stamp["offset"] + 1), expected_score)

    def test_offset_equal_to_stamp(self):
        for stamp in self.game_stamps:
            expected_score = stamp["score"]["home"], stamp["score"]["away"]
            self.assertEqual(get_score(self.game_stamps, stamp["offset"]), expected_score)

    def test_offset_between_stamps(self):
        for i in range(len(self.game_stamps) - 1):
            stamp1 = self.game_stamps[i]
            stamp2 = self.game_stamps[i + 1]
            offset = (stamp1["offset"] + stamp2["offset"]) // 2
            expected_home_score = min(stamp1["score"]["home"], stamp2["score"]["home"])
            expected_away_score = min(stamp1["score"]["away"], stamp2["score"]["away"])
            expected_score = (expected_home_score, expected_away_score)
            self.assertEqual(get_score(self.game_stamps, offset), expected_score)


if __name__ == "__main__":
    unittest.main()
