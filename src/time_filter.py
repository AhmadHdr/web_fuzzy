import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os
import ast  # Untuk evaluasi literal yang aman

def closest_time(same_date, target_time):
    same_date = same_date.copy()
    same_date['TimeDiff'] = same_date['Time'].apply(lambda x: abs((x - target_time).total_seconds()))

    exact_hour = same_date[same_date['Time'].dt.hour == target_time.hour]
    if not exact_hour.empty:
        closest_idx = exact_hour['TimeDiff'].idxmin()
        return exact_hour['TimeDiff'].min(), closest_idx
    else:
        closest_idx = same_date['TimeDiff'].idxmin()
        return same_date['TimeDiff'].min(), closest_idx

def filter_data_by_time(data, *hours):
    results = []
    for current_date in data['Time'].dt.date.unique():
        same_date = data[data['Time'].dt.date == current_date]
        for hour in hours:
            target_time = pd.to_datetime(f'{current_date} {hour}')
            if not same_date.empty:
                min_diff, idx = closest_time(same_date, target_time)
                if min_diff <= 7200:
                    results.append(same_date.loc[idx])
                else:
                    results.append({
                        'Temperature': '-',
                        'pH': '-',
                        'Time': target_time,
                    })
            else:
                results.append({
                    'Temperature': '-',
                    'pH': '-',
                    'Time': target_time,
                })

    result_df = pd.DataFrame(results)
    return result_df

def load_data(weight_file, excel_file):
    try:
        weekly_weights = pd.read_csv(weight_file)
        data = pd.read_excel(excel_file)

        data['Time'] = pd.to_datetime(data['Time'])

        time_filtered = filter_data_by_time(data, '08:00', '18:00')

        # Membuat direktori output jika belum ada
        if not os.path.exists('output'):
            os.makedirs('output')

        time_filtered.to_csv('output/data_terfilter.csv', index=False)
        # print("Data yang telah difilter disimpan ke 'output/data_terfilter.csv'.")

        # print(f"Data berhasil dimuat dan difilter dari {weight_file} dan {excel_file}.")
        return weekly_weights, time_filtered
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat data: {e}")
        raise

def create_antecedent(range_vals, label):
    universe = np.arange(range_vals[0], range_vals[1], range_vals[2])
    return ctrl.Antecedent(universe, label)

def create_consequent(lower_bound, upper_bound, step_size, label):
    universe = np.arange(lower_bound, upper_bound, step_size)
    return ctrl.Consequent(universe, label)

def create_fuzzy_sets(fuzzy_var, membership_params):
    for var, params in membership_params:
        if len(params) == 3:
            mf = fuzz.trimf(fuzzy_var.universe, params)
        elif len(params) == 4:
            mf = fuzz.trapmf(fuzzy_var.universe, params)
        else:
            raise ValueError(f"Parameter fungsi keanggotaan untuk '{var}' tidak valid")
        fuzzy_var[var] = mf
        # Simpan parameter ke term
        fuzzy_var.terms[var].params = [float(p) for p in params]  
    return fuzzy_var

def define_membership_functions(temperatur, ph):
    temperatur_membership_params = [
        ('rendah', [14, 14, 23, 25]),
        ('normal', [23, 25, 29, 31]),
        ('tinggi', [29, 31, 40, 40])
    ]
    temperatur = create_fuzzy_sets(temperatur, temperatur_membership_params)

    ph_membership_params = [
        ('asam', [0, 0, 5, 6.5]),
        ('netral', [5, 6.5, 7.5, 9]),
        ('basa', [7.5, 9, 14, 14])
    ]
    ph = create_fuzzy_sets(ph, ph_membership_params)

    # print("Fungsi keanggotaan untuk temperatur dan pH telah diperbarui.")
    return temperatur, ph

def define_feed_membership_functions(feed_amount, min_feed, max_feed):
    selisih = max_feed - min_feed
    step = selisih / 8

    sedikit_bawah = min_feed
    sedikit_tengah = sedikit_bawah + step * 2
    sedikit_atas = sedikit_tengah + step

    sedang_bawah = sedikit_tengah
    sedang_tengah1 = sedang_bawah + step
    sedang_tengah2 = sedang_tengah1 + step * 2
    sedang_atas = sedang_tengah2 + step

    banyak_bawah = sedang_tengah2
    banyak_tengah = banyak_bawah + step * 2
    banyak_atas = banyak_tengah + step

    membership_params = [
        ('sedikit', [float(sedikit_bawah), float(sedikit_bawah), float(sedikit_tengah), float(sedikit_atas)]),
        ('sedang', [float(sedang_bawah), float(sedang_tengah1), float(sedang_tengah2), float(sedang_atas)]),
        ('banyak', [float(banyak_bawah), float(banyak_tengah), float(banyak_atas), float(banyak_atas)])
    ]

    feed_amount = create_fuzzy_sets(feed_amount, membership_params)
    return feed_amount, membership_params

def define_rules(temperatur, ph, feed_amount):
    rules_list = []
    rules_dict = {}

    rule1 = ctrl.Rule(temperatur['normal'] & ph['asam'], feed_amount['sedang'], label='Rule 1')
    rule1.terms = {'temperatur': 'normal', 'ph': 'asam'}
    rules_list.append(rule1)
    rules_dict['Rule 1'] = 'sedang'

    rule2 = ctrl.Rule(temperatur['normal'] & ph['netral'], feed_amount['banyak'], label='Rule 2')
    rule2.terms = {'temperatur': 'normal', 'ph': 'netral'}
    rules_list.append(rule2)
    rules_dict['Rule 2'] = 'banyak'

    rule3 = ctrl.Rule(temperatur['normal'] & ph['basa'], feed_amount['sedang'], label='Rule 3')
    rule3.terms = {'temperatur': 'normal', 'ph': 'basa'}
    rules_list.append(rule3)
    rules_dict['Rule 3'] = 'sedang'

    rule4 = ctrl.Rule(temperatur['rendah'] & ph['asam'], feed_amount['sedikit'], label='Rule 4')
    rule4.terms = {'temperatur': 'rendah', 'ph': 'asam'}
    rules_list.append(rule4)
    rules_dict['Rule 4'] = 'sedikit'

    rule5 = ctrl.Rule(temperatur['rendah'] & ph['netral'], feed_amount['sedang'], label='Rule 5')
    rule5.terms = {'temperatur': 'rendah', 'ph': 'netral'}
    rules_list.append(rule5)
    rules_dict['Rule 5'] = 'sedang'

    rule6 = ctrl.Rule(temperatur['rendah'] & ph['basa'], feed_amount['sedikit'], label='Rule 6')
    rule6.terms = {'temperatur': 'rendah', 'ph': 'basa'}
    rules_list.append(rule6)
    rules_dict['Rule 6'] = 'sedikit'

    rule7 = ctrl.Rule(temperatur['tinggi'] & ph['asam'], feed_amount['sedikit'], label='Rule 7')
    rule7.terms = {'temperatur': 'tinggi', 'ph': 'asam'}
    rules_list.append(rule7)
    rules_dict['Rule 7'] = 'sedikit'

    rule8 = ctrl.Rule(temperatur['tinggi'] & ph['netral'], feed_amount['sedang'], label='Rule 8')
    rule8.terms = {'temperatur': 'tinggi', 'ph': 'netral'}
    rules_list.append(rule8)
    rules_dict['Rule 8'] = 'sedang'

    rule9 = ctrl.Rule(temperatur['tinggi'] & ph['basa'], feed_amount['sedikit'], label='Rule 9')
    rule9.terms = {'temperatur': 'tinggi', 'ph': 'basa'}
    rules_list.append(rule9)
    rules_dict['Rule 9'] = 'sedikit'

    control_system = ctrl.ControlSystem(rules_list)
    simulation = ctrl.ControlSystemSimulation(control_system)

    # print("Aturan fuzzy telah didefinisikan dan sistem kontrol telah dibuat.")
    return simulation, rules_list, rules_dict

def calculate_feed_bounds(weight, multiplier_min=0.03, multiplier_max=0.05):
    min_feed = weight * multiplier_min
    max_feed = weight * multiplier_max
    return min_feed, max_feed

def calculate_area_and_moment(universe, aggregated_mf, a_values):
    # Fungsi ini tidak lagi digunakan seperti sebelumnya
    # Karena kita akan menggunakan alpha-cut berdasarkan alpha_predikat
    pass

def defuzzify(areas, moments):
    total_area = sum(areas)
    total_moment = sum(moments)
    if total_area != 0:
        z = total_moment / total_area
    else:
        z = 0
    return z

def alpha_cut_intervals(universe, mf, alpha):
    # Mencari interval dari universe di mana mf >= alpha
    # Kemudian mengembalikan min dan max dari interval tersebut
    idx = np.where(mf >= alpha)[0]
    if len(idx) == 0:
        return []
    else:
        # Kita asumsikan mungkin ada lebih dari satu interval.
        # Untuk sederhana, kita gabung semua indeks yang berdekatan menjadi interval tunggal.
        intervals = []
        start = idx[0]
        for i in range(1, len(idx)):
            if idx[i] != idx[i-1] + 1:
                # Terputus, interval selesai
                end = idx[i-1]
                intervals.append((universe[start], universe[end]))
                start = idx[i]
        # Interval terakhir
        end = idx[-1]
        intervals.append((universe[start], universe[end]))
        return intervals

def centroid_defuzzification(universe, mf):
    # Defuzzifikasi centroid sederhana untuk seluruh aggregated_mf
    numerator = np.sum(universe * mf)
    denominator = np.sum(mf)
    if denominator != 0:
        z = numerator / denominator
    else:
        z = 0
    return float(z)

def process_data(weekly_weights, time_filtered, temperatur, ph):
    results = []
    start_date = pd.to_datetime(time_filtered['Time'].iloc[0])

    for index, row in time_filtered.iterrows():
        current_date = pd.to_datetime(row['Time'])
        week_index = (current_date - start_date).days // 7
        week_index = min(week_index, len(weekly_weights.columns) - 2)

        temp = row['Temperature']
        ph_value = row['pH']

        if temp == '-' or ph_value == '-':
            results.append({
                'Time': row['Time'],
                'Temperatur': temp,
                'pH': ph_value,
                'feed_amount': '-',
                'Temperatur_Membership_Params': '-',
                'PH_Membership_Params': '-',
                'Temperatur_Memberships': '-',
                'PH_Memberships': '-',
                'Takaran_Membership_Params': '-',
                'Takaran_Memberships': '-',
                'Alpha_Predikats': '-',
                'a_values': '-'
            })
            continue

        try:
            temp_val = float(temp)
            ph_val = float(ph_value)
        except ValueError:
            results.append({
                'Time': row['Time'],
                'Temperatur': temp,
                'pH': ph_value,
                'feed_amount': '-',
                'Temperatur_Membership_Params': '-',
                'PH_Membership_Params': '-',
                'Temperatur_Memberships': '-',
                'PH_Memberships': '-',
                'Takaran_Membership_Params': '-',
                'Takaran_Memberships': '-',
                'Alpha_Predikats': '-',
                'a_values': '-'
            })
            continue

        print(f"Processing data for {current_date} (Week {week_index + 1})")

        current_week_weight = weekly_weights.iloc[:, week_index + 1].sum()
        current_min_feed, current_max_feed = calculate_feed_bounds(current_week_weight)

        # print(f"Current Week Weight: {current_week_weight}g, Min Feed: {current_min_feed}g, Max Feed: {current_max_feed}g")

        feed_amount = create_consequent(current_min_feed, current_max_feed, 0.001, 'Takaran')
        feed_amount, feed_membership_params = define_feed_membership_functions(feed_amount, current_min_feed, current_max_feed)

        feed_membership_params_dict = {k: [float(vv) for vv in v] for k, v in feed_membership_params}

        simulation, rules_list, rules_dict = define_rules(temperatur, ph, feed_amount)

        # Hitung derajat keanggotaan
        temp_memberships = {}
        for label in temperatur.terms:
            membership_value = fuzz.interp_membership(temperatur.universe, temperatur[label].mf, temp_val)
            temp_memberships[label] = round(float(membership_value), 4)
        ph_memberships = {}
        for label in ph.terms:
            membership_value = fuzz.interp_membership(ph.universe, ph[label].mf, ph_val)
            ph_memberships[label] = round(float(membership_value), 4)

        temperatur_membership_params = {
            term: [round(float(v), 2) for v in temperatur.terms[term].params]
            for term in temperatur.terms
        }
        ph_membership_params = {
            term: [round(float(v), 2) for v in ph.terms[term].params]
            for term in ph.terms
        }

        try:
            activated_rules = []
            aggregated_output = np.zeros_like(feed_amount.universe)
            for rule in rules_list:
                temp_term = rule.terms['temperatur']
                ph_term = rule.terms['ph']
                temp_degree = temp_memberships[temp_term]
                ph_degree = ph_memberships[ph_term]
                activation = min(temp_degree, ph_degree)
                if activation > 0:
                    rule_label = rule.label
                    consequent_label = rules_dict[rule_label]
                    output_mf = feed_amount[consequent_label].mf
                    clipped_mf = np.fmin(activation, output_mf)
                    aggregated_output = np.fmax(aggregated_output, clipped_mf)
                    activated_rules.append({
                        'Rule': rule_label,
                        'Activation': activation,
                        'Temp Degree': temp_degree,
                        'PH Degree': ph_degree,
                        'Consequent': consequent_label
                    })

            if not activated_rules:
                print(f"Tidak ada aturan yang teraktivasi untuk data pada {current_date}.")
                feed = '-'
                feed_memberships_output = '-'
                alpha_predikats = '-'
                a_values_output = '-'
            else:
                # Defuzzifikasi centroid
                feed = centroid_defuzzification(feed_amount.universe, aggregated_output)

                # Hitung membership feed untuk nilai defuzzifikasi
                feed_memberships_output = {}
                for label in feed_amount.terms:
                    membership_value = fuzz.interp_membership(feed_amount.universe, feed_amount[label].mf, feed)
                    feed_memberships_output[label] = round(float(membership_value), 4)

                # Alpha_Predikats
                alpha_predikats = {r['Rule']: round(float(r['Activation']), 4) for r in activated_rules}

                # a_values: Sesuai contoh, kita ingin a_values berisi alpha cuts.
                # Kita akan membentuk alpha-cut intervals untuk setiap alpha level dari aturan teraktivasi.
                # Jika ada beberapa aturan, kita akan membuat satu list of dict:
                # Setiap dict: {'alpha_level': activation, 'a_values': [min_val, max_val, ...]}.
                # Jika ada beberapa interval, kita bisa simpan semua, tetapi contoh hanya menunjukkan satu pasang interval.
                # Kita lakukan iterasi untuk setiap alpha level unik.

                a_values_output = []
                # Ambil alpha unique dan urutkan descending agar yang terbesar dulu
                unique_alphas = sorted({ar['Activation'] for ar in activated_rules}, reverse=True)
                for alpha in unique_alphas:
                    intervals = alpha_cut_intervals(feed_amount.universe, aggregated_output, alpha)
                    # intervals bisa lebih dari satu, untuk contoh kita ambil semua:
                    # Format output: {'alpha_level': alpha, 'a_values': [x_start, x_end]...}
                    # Kita flatten jika ada multiple intervals
                    interval_values = []
                    for (start_val, end_val) in intervals:
                        interval_values.extend([round(float(start_val), 2), round(float(end_val), 2)])
                    if interval_values:
                        a_values_output.append({
                            'alpha_level': round(float(alpha), 3),
                            'a_values': interval_values
                        })

                feed = round(float(feed), 4)

        except Exception as e:
            print(f"Terjadi kesalahan saat komputasi pada data {current_date}: {e}")
            feed = '-'
            feed_memberships_output = '-'
            activated_rules = []
            aggregated_output = None
            a_values_output = '-'
            alpha_predikats = '-'

        temp_memberships = {k: round(float(v), 4) for k, v in temp_memberships.items()}
        ph_memberships = {k: round(float(v), 4) for k, v in ph_memberships.items()}
        feed_memberships_output = {k: round(float(v), 4) for k, v in feed_memberships_output.items()} if feed_memberships_output != '-' else '-'
        feed_membership_params_dict = {k: [round(float(vv), 4) for vv in v] for k, v in feed_membership_params_dict.items()}

        results.append({
            'Time': row['Time'],
            'Temperatur': round(float(temp_val), 2) if temp_val != '-' else '-',
            'pH': round(float(ph_val), 2) if ph_val != '-' else '-',
            'feed_amount': feed,
            'Temperatur_Membership_Params': temperatur_membership_params,
            'PH_Membership_Params': ph_membership_params,
            'Temperatur_Memberships': temp_memberships,
            'PH_Memberships': ph_memberships,
            'Takaran_Membership_Params': feed_membership_params_dict,
            'Takaran_Memberships': feed_memberships_output,
            'Alpha_Predikats': alpha_predikats,
            'a_values': a_values_output
        })

    return results

def save_results_to_csv(results, output_file_recommendations, output_file_inferensi):
    df_results = pd.DataFrame(results)

    # Mengonversi Time ke format yang diinginkan
    df_results['Time'] = pd.to_datetime(df_results['Time']).dt.strftime('%Y-%m-%d %H:%M')

    # Membuat feed_recommendations.csv
    df_feed_recommendations = df_results[['Time', 'Temperatur', 'pH', 'feed_amount']]
    df_feed_recommendations.to_csv(output_file_recommendations, index=False, float_format='%.2f')
    # print(f"Rekomendasi pakan telah disimpan ke {output_file_recommendations}.")

    # Membuat inferensi.csv
    df_inferensi = df_results.drop(columns=['feed_amount'])
    df_inferensi.to_csv(output_file_inferensi, index=False)
    # print(f"Data inferensi telah disimpan ke '{output_file_inferensi}'.")

def main():
    WEIGHT_FILE = 'berat_lobster_weekly.csv'
    EXCEL_FILE = 'Lobster IoT.xlsx'
    OUTPUT_FILE_RECOMMENDATIONS = 'output/feed_recommendations.csv'
    OUTPUT_FILE_INFERENSI = 'output/inferensi.csv'

    # Membuat direktori output jika belum ada
    if not os.path.exists('output'):
        os.makedirs('output')

    weekly_weights, time_filtered = load_data(WEIGHT_FILE, EXCEL_FILE)

    temperatur_range = (14, 40, 0.001)
    ph_range = (4, 14, 0.001)
    temperatur = create_antecedent(temperatur_range, 'Temperatur')
    ph = create_antecedent(ph_range, 'pH')

    temperatur, ph = define_membership_functions(temperatur, ph)

    results = process_data(weekly_weights, time_filtered, temperatur, ph)

    # Memanggil fungsi untuk menyimpan hasil
    save_results_to_csv(results, OUTPUT_FILE_RECOMMENDATIONS, OUTPUT_FILE_INFERENSI)

if __name__ == "__main__":
    main()
