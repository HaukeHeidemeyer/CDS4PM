from __future__ import annotations

import importlib
import json
import logging
import os
import pathlib
from abc import ABC, abstractmethod
import chardet

import pandas as pd


class IDataLoadStrategy(ABC):
    """
    Interface for data load strategies.
    """

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """
        Abstract method to load data from a file and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.
        """
        pass


class BaseDataLoadStrategy(IDataLoadStrategy):
    """
    Base class for data loading strategies.

    This class provides a common interface for loading data from different file formats.
    Subclasses must implement the `load_csv` and `load_json` methods to load data from CSV and JSON files, respectively.
    The `load` method can be used to automatically determine the file format and delegate the loading to the appropriate method.
    """

    def __init__(
        self,
        file_path: str | os.PathLike,
        configuration: str | os.PathLike | None = None,
    ) -> None:
        """
        Initializes the BaseDataLoadStrategy class.

        Args:
            file_path (Union[str, os.PathLike]): The path to the file.
            configuration (Union[str, os.PathLike, None], optional): The path to the configuration file.
        """
        self._file_path = os.path.join(
            pathlib.Path(os.path.abspath(__file__)).parent.absolute(),
            file_path,
        )
        if configuration is not None:
            self._configuration = Configuration.get_configuration(
                table_config_dict=configuration,
            )
        else:
            self._configuration = Configuration.get_configuration(
                data_file_path=file_path,
            )

    def load_csv(self) -> pd.DataFrame:
        """
        Load a CSV file into a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the data from the CSV file.
        """
        if "encoding" not in self._configuration["csv"]:
            with open(self._file_path, "rb") as f:
                encoding = chardet.detect(f.read())["encoding"]
            return pd.read_csv(self._file_path, **self._configuration["csv"], encoding=encoding)
        else:
            return pd.read_csv(self._file_path, **self._configuration["csv"])

    def load_json(self) -> pd.DataFrame:
        """
        Load a JSON file into a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the data from the JSON file.
        """
        raise NotImplementedError("load_json method is not implemented")

    def load(self) -> pd.DataFrame:
        """
        Load data from a file and perform data quality checks.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.

        Raises:
            ValueError: If the file extension is not supported.
            ValueError: If the DataFrame contains NaN values.
            ValueError: If the data type is not set for every attribute.
            ValueError: If the DataFrame is empty.
            ValueError: If the DataFrame contains duplicate rows.
        """
        file_extension = pathlib.Path(self._file_path).suffix.lower()
        if file_extension == ".csv":
            df = self.load_csv()
        elif file_extension == ".json":
            df = self.load_json()
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        # Check for NaN values
        if df.isnull().values.any():
            logging.warning("DataFrame contains NaN values")

        # Check if data type is set for every attribute
        if df.dtypes.isnull().any():
            df.fillna(value="none", inplace=True)

        # Check for data completeness
        if df.empty:
            raise ValueError("DataFrame is empty")

        # Check for data integrity
        if df.duplicated().any():
            logging.warning("DataFrame contains duplicate rows. Dropping duplicates...")
            # Remove duplicate rows in-place
            df.drop_duplicates(inplace=True)

        return df


class Configuration:
    """
    A class for loading and validating configuration files.
    """

    @staticmethod
    def _validate_config(config_data) -> None:
        """
        Validate the configuration data.

        Args:
            config_data: The configuration data to validate.

        Returns:
            None

        Raises:
            ValueError: If the configuration data is invalid.
        """
        # Validate the configuration data TODO
        pass

    @staticmethod
    def get_configuration(
        table_config_dict: dict | None = None,
    ) -> dict:
        """
        Get the configuration data.

        Args:
            table_config_dict (dict | None): The table configuration dictionary.

        Returns:
            dict: The configuration data.

        Raises:
            FileNotFoundError: If the default configuration file is not found.
            ValueError: If the configuration data is invalid.
        """
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "default",
                "table_loading",
                "default_table.json",
            ),
        ) as file:
            default_table_config = json.load(file)

        Configuration._validate_config(default_table_config)
        default_table_config.update(table_config_dict)
        table_config = default_table_config
        Configuration._validate_config(table_config)
        return table_config


class Loader:
    """
    A class that represents a data loader.

    Attributes:
        _strategy (IDataLoadStrategy): The data loading strategy.
        _configuration (dict): The configuration data.
        _data_path (str | os.PathLike): The path to the data file.

    Methods:
        load() -> pd.DataFrame: Loads the data using the set strategy.
        select_strategy() -> IDataLoadStrategy: Selects and returns a data loading strategy based on the configuration file.
    """

    def __init__(
        self,
        data_path: str | os.PathLike,
        configuration: dict,
    ) -> None:
        """
        Initializes the Loader class.

        Args:
            data_path (str | os.PathLike): The path to the data file.
            configuration (dict): The configuration data.
        """
        self._data_path: str | os.PathLike = data_path
        self._configuration = Configuration.get_configuration(configuration)
        self._strategy: IDataLoadStrategy = self.select_strategy()

    def load(self) -> pd.DataFrame:
        """
        Loads the data using the set strategy.

        Returns:
            pd.DataFrame: The loaded data.

        Raises:
            ValueError: If the strategy is not set.
        """
        if self._strategy is None:
            raise ValueError("Strategy not set")
        return self._strategy.load()

    def select_strategy(self) -> IDataLoadStrategy:
        """
        Selects and returns a data loading strategy based on the configuration file.

        Returns:
            IDataLoadStrategy: An instance of the selected data loading strategy.

        Raises:
            ValueError: If the strategy class is not found or cannot be loaded.
        """
        config = self._configuration
        strategy_class_name = config["loader_config"]["loader_strategy"]
        if strategy_class_name.lower() != "default":
            try:
                module = importlib.import_module(
                    "load_strategies_omfs_dataset.custom_loading_strategies",
                )
                strategy_class = getattr(module, strategy_class_name)
            except (ImportError, AttributeError) as exc:
                raise ValueError(
                    "Strategy class not found or cannot be loaded",
                ) from exc
        else:
            strategy_class = BaseDataLoadStrategy

        return strategy_class(
            file_path=self._data_path,
            configuration=self._configuration,
        )


class LoadCaseList(BaseDataLoadStrategy):
    """
    A class representing a strategy for loading case lists from a CSV file.
    """

    def __init__(
        self,
        file_path: str | os.PathLike = None,
        configuration: dict = None,
    ):
        """
        Initializes the LoadCaseList class.

        Args:
            file_path (str | os.PathLike): The path to the CSV file.
            configuration (dict | None): The configuration data.
        """
        super().__init__(
            configuration=configuration,
        )

    def load_csv(self) -> pd.DataFrame:
        """
        Load the CSV file and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded CSV data as a pandas DataFrame.
        """
        encoding: str = self._configuration["csv"]["encoding"]
        delimiter: str = self._configuration["csv"]["delimiter"]
        engine: str = self._configuration["csv"]["engine"]
        assert (
            engine == "python"
        ), "The engine must be set to 'python' for the on_bad_lines parameter to work"

        df: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=self._file_path,
            encoding=encoding,
            delimiter=delimiter,
            engine=engine,
            on_bad_lines=self.join_bad_line,
        )
        return df

    def join_bad_line(self, line):
        """
        Fix a bad line in the CSV file.

        Args:
            line: The bad line in the CSV file.

        Returns:
            list: The fixed line.

        Raises:
            ValueError: If the bad line cannot be fixed.
        """
        file_name: str = pathlib.Path(self._file_path).name
        if file_name == "Pulladi_Fallliste.csv":
            beginning_col = line[0:26]
            mid = [line[27] + "|" + line[28]]
            end_col = line[29:]
            return beginning_col + mid + end_col
        else:
            raise ValueError(
                f"Bad line in file {file_name} could not be fixed",
            )
