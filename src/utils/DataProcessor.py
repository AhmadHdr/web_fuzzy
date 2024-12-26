import numpy as np

import skfuzzy as fuzz
from skfuzzy import control as ctrl

from typing import List
from typing import Tuple
from typing import Union

from FuzzyController import FuzzyParams



class DataProcessor:
    def __init__(self, fuzzy_params: FuzzyParams = FuzzyParams()):
        self.params = fuzzy_params
        self.temperatur = self._create_antecedent(self.params.temp_range, 'Temperatur')
        self.ph = self._create_antecedent(self.params.ph_range, 'pH')
        self._initialize_membership_functions()

    @staticmethod
    def _create_antecedent(range_vals: Tuple[float, float, float], label: str) -> ctrl.Antecedent:
        universe = np.arange(*range_vals)
        return ctrl.Antecedent(universe, label)

    @staticmethod
    def _create_consequent(lower_bound: float, upper_bound: float, step_size: float, label: str) -> ctrl.Consequent:
        universe = np.arange(lower_bound, upper_bound, step_size)
        return ctrl.Consequent(universe, label)

    def _initialize_membership_functions(self):
        """Initialize membership functions for temperature and pH"""
        temp_params = [
            ('rendah', [14, 14, 23, 25]),
            ('normal', [23, 25, 29, 31]),
            ('tinggi', [29, 31, 40, 40])
        ]
        ph_params = [
            ('asam', [0, 0, 5, 6.5]),
            ('netral', [5, 6.5, 7.5, 9]),
            ('basa', [7.5, 9, 14, 14])
        ]
        self.temperatur = self._create_fuzzy_sets(self.temperatur, temp_params)
        self.ph = self._create_fuzzy_sets(self.ph, ph_params)

    @staticmethod
    def _create_fuzzy_sets(fuzzy_var: Union[ctrl.Antecedent, ctrl.Consequent], 
                          membership_params: List[Tuple[str, List[float]]]) -> Union[ctrl.Antecedent, ctrl.Consequent]:
        """Create fuzzy sets with given membership parameters"""
        for var, params in membership_params:
            mf = fuzz.trapmf(fuzzy_var.universe, params) if len(params) == 4 else fuzz.trimf(fuzzy_var.universe, params)
            fuzzy_var[var] = mf
            fuzzy_var.terms[var].params = [float(p) for p in params]
        return fuzzy_var