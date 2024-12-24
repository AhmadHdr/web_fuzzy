# fuzzy_mamdani.py - Implementasi Logika Fuzzy Mamdani
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyMamdani:
    def __init__(self):
        # Definisikan rentang dan aturan fuzzy
        self.input1_range = np.linspace(0, 100, 200)
        self.input2_range = np.linspace(0, 100, 200)
        self.output_range = np.linspace(0, 100, 200)

    def triangular_membership(self, x, a, b, c):
        """Fungsi keanggotaan segitiga"""
        return np.maximum(np.minimum((x - a) / (b - a), (c - x) / (c - b)), 0)

    def calculate_input1_membership(self):
        """Hitung fungsi keanggotaan input pertama"""
        rendah = self.triangular_membership(self.input1_range, 0, 0, 50)
        sedang = self.triangular_membership(self.input1_range, 25, 50, 75)
        tinggi = self.triangular_membership(self.input1_range, 50, 100, 100)

        return {
            'Rendah': rendah,
            'Sedang': sedang,
            'Tinggi': tinggi
        }

    def calculate_input2_membership(self):
        """Hitung fungsi keanggotaan input kedua"""
        # Implementasi serupa dengan input pertama
        rendah = self.triangular_membership(self.input2_range, 0, 0, 50)
        sedang = self.triangular_membership(self.input2_range, 25, 50, 75)
        tinggi = self.triangular_membership(self.input2_range, 50, 100, 100)

        return {
            'Rendah': rendah,
            'Sedang': sedang,
            'Tinggi': tinggi
        }

    def calculate_output_membership(self):
        """Hitung fungsi keanggotaan output"""
        rendah = self.triangular_membership(self.output_range, 0, 0, 50)
        sedang = self.triangular_membership(self.output_range, 25, 50, 75)
        tinggi = self.triangular_membership(self.output_range, 50, 100, 100)

        return {
            'Rendah': rendah,
            'Sedang': sedang,
            'Tinggi': tinggi
        }

    def defuzzification(self, input1, input2):
        """Proses defuzzifikasi dengan metode centroid"""
        # Contoh sederhana - Anda perlu sesuaikan dengan aturan spesifik penelitian Anda
        rule_base = {
            ('Rendah', 'Rendah'): 'Rendah',
            ('Rendah', 'Sedang'): 'Sedang',
            ('Rendah', 'Tinggi'): 'Tinggi',
            ('Sedang', 'Rendah'): 'Sedang',
            ('Sedang', 'Sedang'): 'Sedang',
            ('Sedang', 'Tinggi'): 'Tinggi',
            ('Tinggi', 'Rendah'): 'Tinggi',
            ('Tinggi', 'Sedang'): 'Tinggi',
            ('Tinggi', 'Tinggi'): 'Tinggi'
        }

        # Logika inferensi dan defuzzifikasi
        # Implementasi detail sesuaikan dengan penelitian Anda
        return 75.0  # Contoh output

    def get_inference_steps(self):
        """Dapatkan langkah-langkah inferensi fuzzy"""
        return {
            'fuzzification': 'Proses mengubah input menjadi nilai linguistik',
            'inference': 'Menerapkan aturan fuzzy',
            'defuzzification': 'Mengubah output fuzzy menjadi nilai crisp'
        }