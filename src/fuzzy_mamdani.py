# # fuzzy_mamdani.py - Implementasi Logika Fuzzy Mamdani
# import numpy as np
# import pandas as pd
# import skfuzzy as fuzz
# from skfuzzy import control as ctrl


# class FuzzyMamdani:

#     variable = {"input": [], "output": []}
#     rules = []

#     def __init__(self):
#         # Definisikan rentang dan aturan fuzzy
#         self.variable = {"input":[], "output":[]}

#     @classmethod
#     def add_input_variable(cls, name, min, max, step):
#         """Tambahkan variabel input"""
#         cls.variable["input"].append(ctrl.Antecedent(np.arange(min, max+step, step), name))

#     def add_output_variable(self, name, min, max, step):
#         """Tambahkan variabel output"""
#         self.variable["output"].append(ctrl.Consequent(np.arange(min, max+step, step), name))

#     def triangular_membership(self, x, a, b, c):
#         """Fungsi keanggotaan segitiga"""
#         return np.maximum(np.minimum((x - a) / (b - a), (c - x) / (c - b)), 0)
    
#     def trapezoidal_membership(self, x, a, b, c, d):
#         """Fungsi keanggotaan trapesium"""
#         return np.maximum(np.minimum((x - a) / (b - a), 1, (d - x) / (d - c)), 0)
    
    

#     def calculate_input1_membership(self):
#         """Hitung fungsi keanggotaan input pertama"""
#         rendah = self.triangular_membership(self.input1_range, 0, 0, 50)
#         sedang = self.triangular_membership(self.input1_range, 25, 50, 75)
#         tinggi = self.triangular_membership(self.input1_range, 50, 100, 100)

#         return {
#             'Rendah': rendah,
#             'Sedang': sedang,
#             'Tinggi': tinggi
#         }

#     def calculate_input2_membership(self):
#         """Hitung fungsi keanggotaan input kedua"""
#         # Implementasi serupa dengan input pertama
#         rendah = self.triangular_membership(self.input2_range, 0, 0, 50)
#         sedang = self.triangular_membership(self.input2_range, 25, 50, 75)
#         tinggi = self.triangular_membership(self.input2_range, 50, 100, 100)

#         return {
#             'Rendah': rendah,
#             'Sedang': sedang,
#             'Tinggi': tinggi
#         }

#     def calculate_output_membership(self):
#         """Hitung fungsi keanggotaan output"""
#         rendah = self.triangular_membership(self.output_range, 0, 0, 50)
#         sedang = self.triangular_membership(self.output_range, 25, 50, 75)
#         tinggi = self.triangular_membership(self.output_range, 50, 100, 100)

#         return {
#             'Rendah': rendah,
#             'Sedang': sedang,
#             'Tinggi': tinggi
#         }

#     def defuzzification(self, input1, input2):
#         """Proses defuzzifikasi dengan metode centroid"""
#         # Contoh sederhana - Anda perlu sesuaikan dengan aturan spesifik penelitian Anda
#         rule_base = {
#             ('Rendah', 'Rendah'): 'Rendah',
#             ('Rendah', 'Sedang'): 'Sedang',
#             ('Rendah', 'Tinggi'): 'Tinggi',
#             ('Sedang', 'Rendah'): 'Sedang',
#             ('Sedang', 'Sedang'): 'Sedang',
#             ('Sedang', 'Tinggi'): 'Tinggi',
#             ('Tinggi', 'Rendah'): 'Tinggi',
#             ('Tinggi', 'Sedang'): 'Tinggi',
#             ('Tinggi', 'Tinggi'): 'Tinggi'
#         }

#         # Logika inferensi dan defuzzifikasi
#         # Implementasi detail sesuaikan dengan penelitian Anda
#         return 75.0  # Contoh output

#     def get_inference_steps(self):
#         """Dapatkan langkah-langkah inferensi fuzzy"""
#         return {
#             'fuzzification': 'Proses mengubah input menjadi nilai linguistik',
#             'inference': 'Menerapkan aturan fuzzy',
#             'defuzzification': 'Mengubah output fuzzy menjadi nilai crisp'
#         }
    

# if __name__ == "__main__":
#     # Contoh penggunaan
#     fuzzy = FuzzyMamdani()
#     fuzzy.add_input_variable('temperatur', 0, 100, 0.001)
#     fuzzy.add_input_variable('ph', 0, 14, 0.001)
#     fuzzy.add_output_variable('takaran', 0, 100, 1)

#     fuzzy.input1_range = 70
#     fuzzy.input2_range = 30
#     fuzzy.output_range = fuzzy.defuzzification(fuzzy.input1_range, fuzzy.input2_range)

#     print(fuzzy.calculate_input1_membership())
#     print(fuzzy.calculate_input2_membership())
#     print(fuzzy.calculate_output_membership())
#     print(fuzzy.get_inference_steps())
#     print(fuzzy.output_range)

import pandas as pd

from utils import DataHandler
from utils import DataProcessor
from utils import FeedCalculator
from utils import FuzzyController


def main():
    # Initialize system components
    fuzzy_system = DataProcessor()
    feed_calculator = FeedCalculator(fuzzy_system)
    fuzzy_controller = FuzzyController(fuzzy_system)
    
    # Load input data
    weekly_weights, time_filtered = DataHandler.load_data('berat_lobster_weekly.csv', 'Lobster IoT.xlsx')
    
    # Process each data point
    results = []
    start_date = pd.to_datetime(time_filtered['Time'].iloc[0])
    
    for index, row in time_filtered.iterrows():
        current_date = pd.to_datetime(row['Time'])
        week_index = min((current_date - start_date).days // 7, len(weekly_weights.columns) - 2)
        
        # Skip invalid data points
        if row['Temperature'] == None or row['pH'] == None:
            results.append(DataProcessor.create_empty_result(row['Time']))
            continue
            
        try:
            current_week_weight = weekly_weights.iloc[:, week_index + 1].sum()
            min_feed, max_feed = feed_calculator.calculate_feed_bounds(current_week_weight)
            
            feed_amount, feed_params = feed_calculator.define_feed_membership_functions(min_feed, max_feed)
            simulation, rules_list, rules_dict = fuzzy_controller.define_rules(feed_amount)
            
            result = DataProcessor.process_single_record(
                row, fuzzy_system, feed_amount, feed_params, rules_list, rules_dict
            )
            results.append(result)
            
        except Exception as e:
            print(f"Error processing data for {current_date}: {e}")
            results.append(DataProcessor.create_empty_result(row['Time']))
    
    # Save results
    DataHandler.save_results(results)

if __name__ == "__main__":
    main()