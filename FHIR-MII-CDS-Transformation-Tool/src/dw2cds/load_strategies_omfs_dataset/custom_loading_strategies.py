from __future__ import annotations

import os
import pathlib

import pandas as pd
from loader import BaseDataLoadStrategy


class LoadDiag(BaseDataLoadStrategy):
    """
    A class representing a strategy for loading diagnoeses and procedure from its corresponding CSV file.
    """

    def __init__(
        self,
        file_path: str | os.PathLike = None,
        configuration: str | os.PathLike | None = None,
    ):
        """
        Initializes the LoadCaseList class.

        Args:
            file_path (str | os.PathLike): The path to the CSV file.
            configuration (Optional[str | os.PathLike]): The path to the configuration file.
        """
        default_file_path = os.path.join(
            "dataWH_tables",
            "Pul_x1280dia_Diag_Pro.csv",
        )
        super().__init__(
            file_path=file_path or default_file_path,
            configuration=configuration,
        )
        self.filter_column_name = "DCAOFF"
        self.filter_value_starts_with = "ICD"
        self._df = None

    def load_csv(self) -> pd.DataFrame:
        """
        Load the CSV file and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded CSV data as a pandas DataFrame.
        """
        encoding: str = self._configuration["csv"].get("encoding")
        delimiter: str = self._configuration["csv"]["delimiter"]
        engine: str = self._configuration["csv"]["engine"]
        assert (
            engine == "python"
        ), "The engine must be set to 'python' for the on_bad_lines parameter to work"

        self._df: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=self._file_path,
            encoding=encoding,
            delimiter=delimiter,
            engine=engine,
            on_bad_lines=self.join_bad_line,
            encoding_errors="replace",
        )
        return self.filter(self.filter_column_name, self.filter_value_starts_with)

    def filter(self, columnname, value_startswith):
        """
        Filter the dataframe based on the given column name and value.

        Args:
            columnname: The column name to filter on.
            value_startswith: The value to filter on.

        Returns:
            pd.DataFrame: The filtered dataframe.
        """
        return self._df[self._df[columnname].str.startswith(value_startswith)]

    def join_bad_line(self, line):
        """
        Fix a bad line in the CSV file.

        Args:
            line: The bad line in the CSV file.

        Returns:
            str: The fixed line.

        Raises:
            ValueError: If the bad line cannot be fixed.
        """
        file_name: str = pathlib.Path(self._file_path).name
        if file_name == "Pul_x1280dia_Diag_Pro.csv":
            beginning_col = line[0:26]
            mid = [line[27] + "|" + line[28]]
            end_col = line[29:]
            return beginning_col + mid + end_col
        else:
            raise ValueError(
                f"Bad line in file {file_name} could not be fixed",
            )


class LoadProc(LoadDiag):
    def __init__(
        self,
        file_path: str | os.PathLike = None,
        configuration: str | os.PathLike | None = None,
    ):
        """
        Initializes the LoadCaseList class.

        Args:
            file_path (str | os.PathLike): The path to the CSV file.
            configuration (Optional[str | os.PathLike]): The path to the configuration file.
        """
        default_file_path = os.path.join(
            "dataWH_tables",
            "Pul_x1280dia_Diag_Pro.csv",
        )
        super().__init__(
            file_path=file_path or default_file_path,
            configuration=configuration,
        )
        self.filter_column_name = "DCAOFF"
        self.filter_value_starts_with = "OPS"


class LoadLabTableRequest(BaseDataLoadStrategy):
    def __init__(
        self,
        file_path: str | os.PathLike = None,
        configuration: str | os.PathLike | None = None,
    ):
        super().__init__(
            file_path=file_path or self.default_file_path,
            configuration=configuration,
        )

        def load_csv(self) -> pd.DataFrame:
            return filter_first_row_per_group(super().load_csv())

        def filter_first_row_per_group(self):
            # Group the DataFrame based on the 'DRE' column
            grouped_df = self.df.groupby("DRE")

            # Get the first row of each group
            filtered_df = grouped_df.first()

            # Return the resulting DataFrame
            return filtered_df

class USUTableWindow(BaseDataLoadStrategy):
    def __init__(
        self,
        file_path: str | os.PathLike = None,
        configuration: str | os.PathLike | None = None,
    ):
        super().__init__(
            file_path=file_path or self.default_file_path,
            configuration=configuration,
        )

    def load_csv(self) -> pd.DataFrame:
        df = super().load_csv()
        mask = df['STAD'].notna() & df['STOD'].notna()
        return df[mask]

class USUTableDate(BaseDataLoadStrategy):
    def __init__(
            self,
            file_path: str | os.PathLike = None,
            configuration: str | os.PathLike | None = None,
    ):
        super().__init__(
            file_path=file_path or self.default_file_path,
            configuration=configuration,
        )

    def load_csv(self) -> pd.DataFrame:
        df = super().load_csv()
        mask = df['STAD'].notna() & df['STOD'].notna()
        return df[~mask]