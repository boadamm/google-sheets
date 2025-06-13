"""File parser module for CSV and XLSX files.

This module provides functionality to parse and clean data from
CSV and Excel files, returning pandas DataFrames.
"""

from pathlib import Path
from typing import Union
import pandas as pd


class UnsupportedFileTypeError(Exception):
    """Raised when attempting to parse an unsupported file type."""

    pass


def parse_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """Parse a CSV or XLSX file and return a cleaned DataFrame.

    Args:
        file_path: Path to the file to parse (CSV or XLSX)

    Returns:
        pandas.DataFrame: Cleaned DataFrame with the file data

    Raises:
        FileNotFoundError: If the file doesn't exist
        UnsupportedFileTypeError: If the file type is not supported
        ValueError: If the file cannot be parsed
    """
    file_path = Path(file_path)

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Determine file type and parse accordingly
    file_extension = file_path.suffix.lower()

    try:
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {file_extension}. "
                "Supported types: .csv, .xlsx, .xls"
            )
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty or contains no data: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing file {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error reading file {file_path}: {e}")

    # Clean the DataFrame
    cleaned_df = _clean_dataframe(df)

    return cleaned_df


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a DataFrame by removing empty rows and columns.

    Args:
        df: The DataFrame to clean

    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    # Remove completely empty rows and columns
    df = df.dropna(how="all")  # Remove rows that are entirely NaN
    df = df.dropna(axis=1, how="all")  # Remove columns that are entirely NaN

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].astype(str).str.strip()
        # Convert back 'nan' strings to actual NaN
        df[col] = df[col].replace("nan", pd.NA)

    # Reset index after dropping rows
    df = df.reset_index(drop=True)

    return df
