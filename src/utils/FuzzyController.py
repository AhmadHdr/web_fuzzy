from typing import Dict
from typing import List
from typing import Tuple
from skfuzzy import control as ctrl
from dataclasses import dataclass

from DataProcessor import DataProcessor


@dataclass
class FuzzyParams:
    """Class to store fuzzy system parameters"""
    temp_range: Tuple[float, float, float] = (14, 40, 0.001)
    ph_range: Tuple[float, float, float] = (4, 14, 0.001)
    feed_multiplier_min: float = 0.03
    feed_multiplier_max: float = 0.05


class FuzzyController:
    def __init__(self, fuzzy_system: DataProcessor):
        self.fuzzy_system = fuzzy_system

    def define_rules(self, feed_amount: ctrl.Consequent) -> Tuple[ctrl.ControlSystemSimulation, List[ctrl.Rule], Dict[str, str]]:
        """Define fuzzy rules for the system"""
        rule_definitions = [
            ('normal', 'asam', 'sedang'),
            ('normal', 'netral', 'banyak'),
            ('normal', 'basa', 'sedang'),
            ('rendah', 'asam', 'sedikit'),
            ('rendah', 'netral', 'sedang'),
            ('rendah', 'basa', 'sedikit'),
            ('tinggi', 'asam', 'sedikit'),
            ('tinggi', 'netral', 'sedang'),
            ('tinggi', 'basa', 'sedikit')
        ]
        
        rules_list = []
        rules_dict = {}
        
        for i, (temp, ph, feed) in enumerate(rule_definitions, 1):
            rule = ctrl.Rule(
                self.fuzzy_system.temperatur[temp] & self.fuzzy_system.ph[ph],
                feed_amount[feed],
                label=f'Rule {i}'
            )
            rule.terms = {'temperatur': temp, 'ph': ph}
            rules_list.append(rule)
            rules_dict[f'Rule {i}'] = feed

        control_system = ctrl.ControlSystem(rules_list)
        return ctrl.ControlSystemSimulation(control_system), rules_list, rules_dict
