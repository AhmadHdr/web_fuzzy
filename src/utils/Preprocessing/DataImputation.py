from typing import Optional, Tuple
import pandas as pd


def correlation_check(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.DataFrame]:
    """
    Interpolasi data berbasis waktu dan menghitung matriks korelasi antara kolom 'Temperature' dan 'pH'.

    Args:
        df (pd.DataFrame): DataFrame dengan kolom 'Time', 'Temperature', dan 'pH'.
        
    Returns:
        Tuple: Tiga elemen tuple:
            - pd.Series: Kolom 'Temperature' setelah interpolasi
            - pd.Series: Kolom 'pH' setelah interpolasi
            - pd.DataFrame: Matriks korelasi antara 'Temperature' dan 'pH'
    """


    print("\nMatriks korelasi setelah interpolasi awal:")
    correlation_matrix = df[['Temperature', 'pH']].corr()
    print(correlation_matrix)

    return df["Temperature"], df["pH"], correlation_matrix

def interpolation(df_asal: pd.DataFrame):

    df = df_asal.copy()

    # Pastikan 'Time' sebagai indeks
    df.set_index('Time', inplace=True)

    # Lakukan interpolasi berbasis waktu
    df['Temperature'] = round(df['Temperature'].interpolate(method='time'), 2)
    df['pH'] = round(df['pH'].interpolate(method='time'), 2)
    
    # Reset indeks setelah interpolasi
    # df.reset_index(inplace=True)

    return df

def impute_missing_values(
        df: pd.DataFrame, 
        method: str = "median", 
        fill_value: Optional[Tuple[Optional[float], Optional[float]]] = (None, None), 
        verbose: bool = False
        ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Imputasi nilai yang hilang pada DataFrame berdasarkan metode yang dipilih.

    Args:
        df (pd.DataFrame): DataFrame input untuk memeriksa dan mengimputasi nilai yang hilang.
        method (str): Metode imputasi untuk nilai yang hilang. Pilihan:
            - "mean": Isi dengan nilai rata-rata kolom.
            - "median": Isi dengan nilai median kolom.
            - "value": Isi dengan nilai spesifik yang diberikan dalam `fill_value`.
        fill_value (Tuple[Optional[float], Optional[float]], optional): Nilai spesifik untuk mengisi jika metode adalah "value". Defaultnya adalah `(None, None)`.
        verbose (bool): Jika True, mencetak informasi tentang nilai yang hilang dan imputasi yang dilakukan.

    Returns:
        Tuple: Dua elemen tuple:
            - pd.DataFrame: DataFrame baru dengan nilai yang hilang sudah diimputasi.
            - pd.DataFrame: Matriks korelasi antara 'Temperature' dan 'pH' setelah imputasi.
    
    Raises:
        ValueError: Jika metode yang dipilih tidak valid atau `fill_value` tidak diberikan untuk metode 'value'.
    """
    
    # Periksa apakah ada nilai yang hilang
    if df.isnull().sum().sum() == 0:
        if verbose:
            print("Tidak ada nilai yang hilang pada DataFrame.")
        return df, pd.DataFrame()  # Tidak perlu imputasi jika tidak ada nilai yang hilang
    
    if method not in ["mean", "median", "value"]:
        raise ValueError("Metode tidak valid. Pilih 'mean', 'median', atau 'value'.")
        
    if verbose:
        print("Nilai yang hilang ditemukan. Memulai imputasi...")
        print(df.isnull().sum())

    imputed_df = df.copy()  # Membuat salinan DataFrame agar tidak memodifikasi df asli
    # imputed_df["Temperature"], imputed_df["pH"] = correlation_check(imputed_df)

    # Melakukan imputasi berdasarkan metode yang dipilih
    if method == "mean":
        imputed_df['Temperature'] = imputed_df['Temperature'].fillna(imputed_df['Temperature'].mean())
        imputed_df['pH'] = imputed_df['pH'].fillna(imputed_df['pH'].mean())
        if verbose:
            print("Imputasi selesai menggunakan nilai rata-rata.")
    elif method == "median":
        imputed_df['Temperature'] = imputed_df['Temperature'].fillna(imputed_df['Temperature'].median())
        imputed_df['pH'] = imputed_df['pH'].fillna(imputed_df['pH'].median())
        if verbose:
            print("Imputasi selesai menggunakan nilai median.")
    elif method == "value":
        if fill_value == (None, None):
            raise ValueError("`fill_value` harus diberikan saat metode adalah 'value'.")
        imputed_df['Temperature'] = imputed_df['Temperature'].fillna(fill_value[0])
        imputed_df['pH'] = imputed_df['pH'].fillna(fill_value[1])
        if verbose:
            print(f"Imputasi selesai menggunakan nilai yang ditentukan: {fill_value}.")

    return imputed_df

if __name__ == "__main__":

    from DataManager import load_data
    from DataManager import save_data
    from PathManager import OUTPUT_DIR
        
    # Membaca data dari file CSV
    time_filtered_df = load_data(OUTPUT_DIR / 'time_filtered.csv')

    # Konversi kolom 'Time' menjadi datetime
    time_filtered_df['Time'] = pd.to_datetime(time_filtered_df['Time'])

    # Imputasi
    imputed = impute_missing_values(interpolation(time_filtered_df),method='median', verbose=True)
    

    # Save to file
    name_saved = 'imputed_data'
    file_format = 'csv'
    save_data(imputed, output_path=OUTPUT_DIR, saved_name=name_saved, file_format=file_format)
    





