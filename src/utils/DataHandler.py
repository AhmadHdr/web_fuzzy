from typing import List
from typing import Dict
from typing import Tuple
from datetime import datetime

import pandas as pd
import os

from Preprocessing import BASE_DIR
from Preprocessing import DATA_DIR
from Preprocessing import OUTPUT_DIR

class DataHandler:
    @staticmethod
    def load_data(weight_file: str, raw_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and preprocess input data"""
        try:
            weekly_weights = pd.read_csv(weight_file)
            data = pd.read_csv(raw_file)
            data['Time'] = pd.to_datetime(data['Time'])
            
            time_filtered = DataHandler._filter_data_by_time(data, '08:00', '18:00')
            
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            time_filtered.to_csv(OUTPUT_DIR / 'data_terfilter.csv', index=False)
            
            return weekly_weights, time_filtered
        except Exception as e:
            raise Exception(f"Error loading data: {e}")

    @staticmethod
    def _filter_data_by_time(data: pd.DataFrame, *hours: str) -> pd.DataFrame:
        """Filter data for specific hours"""
        def _closest_time(same_date: pd.DataFrame, target_time: datetime) -> Tuple[float, int]:
            same_date = same_date.copy()
            same_date['TimeDiff'] = same_date['Time'].apply(lambda x: abs((x - target_time).total_seconds()))
            
            exact_hour = same_date[same_date['Time'].dt.hour == target_time.hour]
            if not exact_hour.empty:
                closest_idx = exact_hour['TimeDiff'].idxmin()
                return exact_hour['TimeDiff'].min(), closest_idx
            
            closest_idx = same_date['TimeDiff'].idxmin()
            return same_date['TimeDiff'].min(), closest_idx

        results = []
        for current_date in data['Time'].dt.date.unique():
            same_date = data[data['Time'].dt.date == current_date]
            for hour in hours:
                target_time = pd.to_datetime(f'{current_date} {hour}')
                if not same_date.empty:
                    min_diff, idx = _closest_time(same_date, target_time)
                    if min_diff <= 7200:  # 2 hours threshold
                        results.append(same_date.loc[idx])
                    else:
                        results.append({'Temperature': None, 'pH': None, 'Time': target_time})
                else:
                    results.append({'Temperature': None, 'pH': None, 'Time': target_time})
        
        return pd.DataFrame(results)

    @staticmethod
    def save_results(results: List[Dict], output_dir: str = OUTPUT_DIR) -> None:
        """Save processing results to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        df_results = pd.DataFrame(results)
        df_results['Time'] = pd.to_datetime(df_results['Time']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Save feed recommendations
        df_feed = df_results[['Time', 'Temperatur', 'pH', 'feed_amount']]
        df_feed.to_csv(f'{output_dir}/feed_recommendations.csv', index=False, float_format='%.2f')
        
        # Save inference data
        df_inferensi = df_results.drop(columns=['feed_amount'])
        df_inferensi.to_csv(f'{output_dir}/inferensi.csv', index=False)