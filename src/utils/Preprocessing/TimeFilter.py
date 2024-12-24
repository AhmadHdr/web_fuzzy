from DataManager import load_data
from DataManager import save_data
from DataManager import to_datetime
from DataManager import pd
from DataManager import np

from PathManager import Path
from PathManager import DATA_DIR
from PathManager import OUTPUT_DIR

def closest_time(same_date, target_time):

    # same_date.loc['Time'] = same_date['Time'].apply(lambda x: abs((x - target_time).total_seconds()))
    # Untuk mencegah unexpected changed karena menggunakan data asli
    # read this : https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas

    date_chosen = same_date.copy()

    date_chosen['TimeDiff'] = date_chosen['Time'].apply(lambda x: abs((x - target_time).total_seconds()))

    # Mengambil data dari jam yang sama
    exact_hour = date_chosen[date_chosen['Time'].dt.hour == target_time.hour]
    
    if not exact_hour.empty:
        closest_idx = exact_hour['TimeDiff'].idxmin()
        return exact_hour['TimeDiff'].min(), closest_idx
    else:
        closest_idx = date_chosen['TimeDiff'].idxmin()
        return date_chosen['TimeDiff'].min(), closest_idx

def filter_data_by_time(data: pd.DataFrame, time_range: list[2], time_step: float=1):
    
    # Pastikan time_range adalah list atau tuple
    if not isinstance(time_range, (list, tuple)):
        raise TypeError("Parameter 'time_range' harus berupa list atau tuple.")
    
    # Pastikan setiap elemen dalam time_range adalah integer atau float
    if not all(isinstance(item, (int, float)) for item in time_range):
        raise ValueError("Semua elemen dalam 'time_range' harus berupa integer atau float.")
    

    # Membuat list waktu "00:00" - "23:30" dengan step setiap 30 menit
    hours = np.arange(time_range[0], time_range[1], time_step)
    chosen_hours = []
    for hour in hours:        
        if hour.is_integer(): 
            if hour < 10 : chosen_hours.append(f"0{int(hour)}:00")
            else: chosen_hours.append(f"{int(hour)}:00")
        else:
            if hour < 10 : chosen_hours.append(f"0{int(hour)}:30")
            else: chosen_hours.append(f"{int(hour)}:30")


    results = []
    empty_counter = 0

    # Didalam data[Time].dt.date terdapat banyak tanggal yang sama (hanya tanggal)
    # maka digunakan .unique() untuk mengambil 1 data dari data yang sama
    for current_date in data['Time'].dt.date.unique():

        # Mengambil data temperatur dan pH pada baris current_date
        same_date = data[data['Time'].dt.date == current_date]

        for hour in chosen_hours:
            target_time = to_datetime(f'{current_date} {hour}')
            if not same_date.empty:
                min_diff, idx = closest_time(same_date, target_time)
                if min_diff <= 600: # rentang waktu 10 menit
                    results.append(same_date.loc[idx])
                else:
                    empty_counter += 1
                    results.append({
                        'Temperature': None,
                        'pH': None,
                        'Time': target_time,
                    })
            else:
                empty_counter += 1
                results.append({
                    'Temperature': None,
                    'pH': None,
                    'Time': target_time,
                })

    result_df = pd.DataFrame(results)
    return result_df, empty_counter




if __name__ == "__main__":

    # Datasets path
    raw_data_path = DATA_DIR / "dataset.csv"
    output_name = "time_filtered"

    try:
        data = load_data(raw_data_path)
        data['Time'] = to_datetime(data['Time'])

        time_filtered, empty_rows = filter_data_by_time(data, [0, 24], time_step=0.5)

        # Urutkan dan set indeks pada salinan
        time_filtered.sort_values(by='Time', inplace=True)
        time_filtered.set_index('Time', inplace=True)

        save_data(time_filtered, OUTPUT_DIR, output_name)
        print(f"Jumlah data yang kosong ada {empty_rows} dari {len(time_filtered)} data")

    except Exception as e:
        print(f"Terjadi kesalahan saat memuat data: {e}")
        raise

