from typing import List, Tuple
import skfuzzy.control as ctrl

from DataProcessor import DataProcessor



class FeedCalculator:
    def __init__(self, fuzzy_system: DataProcessor):
        self.fuzzy_system = fuzzy_system

    def calculate_feed_bounds(self, weight: float) -> Tuple[float, float]:
        """Calculate minimum and maximum feed amounts based on weight"""
        min_feed = weight * self.fuzzy_system.params.feed_multiplier_min
        max_feed = weight * self.fuzzy_system.params.feed_multiplier_max
        return min_feed, max_feed

    def define_feed_membership_functions(self, min_feed: float, max_feed: float) -> Tuple[ctrl.Consequent, List[Tuple[str, List[float]]]]:
        """Define membership functions for feed amount"""
        feed_amount = self.fuzzy_system._create_consequent(min_feed, max_feed, 0.001, 'Takaran')
        step = (max_feed - min_feed) / 8

        params = self._calculate_membership_params(min_feed, step)
        feed_amount = self.fuzzy_system._create_fuzzy_sets(feed_amount, params)
        return feed_amount, params

    @staticmethod
    def _calculate_membership_params(min_feed: float, step: float) -> List[Tuple[str, List[float]]]:
        """Calculate membership parameters for feed amount"""
        positions = {
            'sedikit': [0, 0, 2, 3],
            'sedang': [2, 3, 5, 6],
            'banyak': [5, 7, 8, 8]
        }
        
        return [(label, [min_feed + pos * step for pos in points]) 
                for label, points in positions.items()]