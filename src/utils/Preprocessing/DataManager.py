import pandas as pd
from pandas import to_datetime
import numpy as np
from numpy import arange

from PathManager import Path


def load_data(source_path: Path) -> pd.DataFrame:
    """
    Load a dataset file based on its file format.

    Args:
        source_path (Path): Path object representing the path to the source file.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the loaded dataset.

    Raises:
        ValueError: If the file format is not supported or if the file does not exist.
    """
    # Validasi apakah file ada
    if not source_path.exists():
        raise ValueError(f"File not found: {source_path}")

    # Dapatkan ekstensi file
    file_format = source_path.suffix.lower()

    # Load data berdasarkan format
    if file_format == '.csv':
        return pd.read_csv(source_path)
    elif file_format in ['.xls', '.xlsx']:
        return pd.read_excel(source_path)
    elif file_format == '.json':
        return pd.read_json(source_path)
    else:
        raise ValueError(f"File format '{file_format}' is not supported!")


def save_data(df: pd.DataFrame, output_path: Path, saved_name: str, file_format: str = 'csv') -> Path:
    """
    Save a Pandas DataFrame to a file.

    Args:
        df (pd.DataFrame): DataFrame containing 'Temperature', 'pH', and 'Time' columns.
        output_path (Path): Path to the directory where the file will be saved.
        saved_name (str): Name of the output file.
        file_format (str): File format of the output file

    Returns:
        Path: The full path of the saved CSV file.

    Raises:
        ValueError: If the DataFrame is empty or if `output_path` is not valid.
        ValueError: If the file format is not supported or if the file does not exist.
    """

    # Validasi DataFrame dan output_path
    if df.empty:
        raise ValueError("DataFrame kosong. Tidak ada data yang disimpan.")
    
    # required_columns = {'Time', 'Temperature', 'pH'}
    # if not required_columns.issubset(df.columns):
    #     print(f"Kolom dalam DataFrame:", df.columns)
    #     raise ValueError(f"DataFrame harus memiliki kolom: {', '.join(required_columns)}")
    
    # Pastikan direktori output ada
    output_path.mkdir(parents=True, exist_ok=True)

    # Simpan file
    if file_format == 'csv':
        file_path = output_path / f"{saved_name}.{file_format}"
        df.to_csv(file_path)
    elif file_format in ['xls', 'xlsx']:
        file_path = output_path / f"{saved_name}.{file_format}"
        df.to_excel(file_path)
    elif file_format == 'json':
        file_path = output_path / f"{saved_name}.{file_format}"
        df.to_json(file_path)
    else:
        raise ValueError(f"File format '{file_format}' is not supported!")
    
    print(f"Data berhasil disimpan ke {file_path}.")

    return file_path