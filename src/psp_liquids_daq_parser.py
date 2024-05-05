from numpy import float64
from numpy.typing import NDArray
from nptdms import TdmsFile, TdmsGroup
import pickle
import numpy as np
# import tkinter as tk
# from tkinter import filedialog
import os

import pandas as pd
from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from helpers import compileChannels, convertStringTimestamp, getTime, tdmsFilenameToSeconds

def parseTDMS(
    dev_num: int, start_time_unix_ms: int = 0, file_path_custom: str = "", dev_group: str = "Data (1000.000000 Hz)"
) -> dict[str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]]:
    """## Parse a TDMS file (or an equivalent pickle file)
    ### Arguments:
    - `dev_num` (Type: `int`): dev box number (i.e: the `5` or `6` in dev5 or dev6)
    - `start_time_unix_ms` (Type: `int`): unix timestamp in milliseconds indicating recording start time. Only required if not reading from a pickle file.
    - (Optional) `file_path_custom` (Type: `str`): the dynamic file path to a `.TDMS` file (use this in case you don't want to keep selecting the tdms file to parse every time you run the script)
    - (Optional) `dev_group` (Type: `str`): the TDMS group header. You usually don't have to touch this unless the data isn't high frequency sampling data
    ### Description
    If `file_path_custom` isn't specified, the file picker dialog comes up to select a tdms file. Then, we check to see if there's an equivalent pickle file in the same directory as the chosen tdms file.
    If there's a pickle file, we parse that. Otherwise, we parse the TDMS file and save the resulting object to a pickle file for later.
    """
    if file_path_custom == "":
        # root = tk.Tk()
        # root.withdraw()
        # filepath: str = filedialog.askopenfilename(
        #     initialdir="./", title="Choose Dev" + str(dev_num) + " TDMS file"
        # )
        print(
            f'to skip the filepicker, use "parseTDMS({dev_num}, file_path_custom=)"'
        )
    else:
        filepath = file_path_custom
    pickle_filepath: str = filepath[:-5] + ".pickle"
    if os.path.exists(pickle_filepath):
        print("unpickling...")
        with open(pickle_filepath, "rb") as f:
            unpickledData: dict[
                str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]
            ] = pickle.loads(f.read())
            print("unpickled data")
            return unpickledData
    else:
        channel_data_map: dict[
            str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]
        ] = {}
        tdms_file: TdmsFile = TdmsFile.read(filepath)
        group: TdmsGroup = tdms_file[dev_group]
        dev5_channels = compileChannels(group.channels())
        channel_data_map.update(dev5_channels[0])
        channel_data_map.update(dev5_channels[1])
        if (start_time_unix_ms == 0):
            start_time_unix_ms = tdmsFilenameToSeconds(os.path.basename(filepath)) * 1000
        channel_data_map["time"] = getTime(channel_data_map, dev_group, start_time_unix_ms)
        with open(pickle_filepath, "wb") as f:
            pickle.dump(channel_data_map, f, pickle.HIGHEST_PROTOCOL)
        print(
            f'conversion done!\n\n\nNext time you want to run the converter, consider calling the function with: "parseTDMS({dev_num}, file_path_custom={pickle_filepath[:-7] + ".tdms"})"'
        )
        return channel_data_map

def extendDatasets(
    channel_data: dict[str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]], binary_channel_prefixes: tuple[str] = ("pi-", "reed-")
) -> tuple[list[str], int, dict[str, list[float]]]:
    """## Extend combined datasets
    Basically makes all the datasets of all the channel the same length. Uses the numpy "edge" method for the time dataset. Uses constant values for channel data (o for analog data, 0.5 for binary data)

    For example, if you had:
    ```
    {
    "channel1": [0, 1, 2],
    "channel2": [23, 234, 235, 12, 456]
    }
    ```
    this function would return:
    ```
    {
    "channel1": [0, 1, 2, 0, 0],
    "channel2": [23, 234, 235, 12, 456]
    }
    ```

    ### Arguments
    - `channel_data` (Type: `dict[str, AnalogChannelData | DigitalChannelData | list[float]]`): the output of `parseTDMS` or multiple `parseTDMS`s
    - (Optional) `binary_channel_prefixes` (Type: `tuple[str]`): The channel name prefixes that indicate if the channel is a binary output channel
    ### Outputs (`tuple`)
    - `list[str]`: the list of all channel names that were provided
    - `int`: max length of datasets
    - `dict[str, AnalogChannelData | DigitalChannelData | list[float]]`: the extended data in the same format as outputted by `parseTDMS`
    """
    # get all the available channel names
    available_channels = list(channel_data.keys())

    # get the length of the largest dataset
    total_length: int = 0
    for channel in available_channels:
        if channel != "time" and len(channel_data[channel].data) > total_length:
            total_length = len(channel_data[channel].data)

    first_time: float = channel_data["time"][0]
    last_time: float = channel_data["time"][-1]
    available_channels = []
    df = pd.DataFrame.from_dict({"time": channel_data["time"]})
    for dataset in channel_data:
        if dataset != "time":
            new_data = np.array(channel_data[dataset].data.tolist())
            temp_time = channel_data["time"][:len(new_data)]
            if(hasattr(channel_data[dataset], "time")):
                temp_time = np.array(channel_data[dataset].time.tolist())
            new_df = pd.DataFrame.from_dict(
                {
                    "temp_time": temp_time,
                    dataset: new_data,
                }
            )
            new_df.drop(new_df[new_df['temp_time'] < first_time].index, inplace=True)
            new_df.drop(new_df[new_df['temp_time'] > last_time].index, inplace=True)
            new_df.dropna(inplace=True)
            merged_df = pd.merge_asof(
                df.sort_values("time"),
                new_df.sort_values("temp_time"),
                left_on="time",
                right_on="temp_time",
                direction="nearest",
                tolerance=5
            )
            merged_df.drop("temp_time", axis=1, inplace=True)
            df = merged_df
            available_channels.append(dataset)
            print("extended: " + dataset)
    max_length = len(df.index)
    print("packaging datasets...")
    dict_from_df = df.to_dict("list")
    print("finished packaging datasets")
    return (available_channels, max_length, dict_from_df)

def parseCSV(
    start_time_unix_ms: int = 0, file_path_custom: str = ""
) -> dict[str, SensorNetData]:
    """## Parse a CSV file (or an equivalent pickle file)
    ### Arguments:
    - `start_time_unix_ms` (Type: `int`): unix timestamp in milliseconds indicating recording start time. Only required if not reading from a pickle file.
    - (Optional) `file_path_custom` (Type: `str`): the dynamic file path to a `.TDMS` file (use this in case you don't want to keep selecting the tdms file to parse every time you run the script)
    ### Description
    If `file_path_custom` isn't specified, the file picker dialog comes up to select a reduced csv file from sensornet. Then, we check to see if there's an equivalent pickle file in the same directory as the chosen csv file.
    If there's a pickle file, we parse that. Otherwise, we parse the csv file and save the resulting object to a pickle file for later.
    """
    if file_path_custom == "":
        # root = tk.Tk()
        # root.withdraw()
        # filepath: str = filedialog.askopenfilename(
        #     initialdir="./", title="Choose Reduced Sensornet CSV file"
        # )
        print(
            'to skip the filepicker, use "parseCSV(file_path_custom=)"'
        )
    else:
        filepath = file_path_custom
    pickle_filepath: str = filepath[:-4] + ".pickle"
    if os.path.exists(pickle_filepath):
        print("unpickling...")
        with open(pickle_filepath, "rb") as f:
            unpickledData: dict[
                str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]
            ] = pickle.loads(f.read())
            print("unpickled data")
            return unpickledData
    else:
        channel_data_map: dict[
            str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]
        ] = {}

        df: pd.DataFrame = pd.read_csv(filepath)
        channel_names: list[str] = df.columns.to_list()
        print("converting timestamps...")
        for channel_name in channel_names:
            if "_time" in channel_name and "-" in str(df[channel_name][3]):
                df[channel_name] = df[channel_name].apply(lambda x: convertStringTimestamp(x, "UTC"))
        df[channel_names] = df[channel_names].astype('float64')
        for i in range(1,len(channel_names),2):
            channel: str = channel_names[i]
            timeArray: NDArray[float64] = df.iloc[:,i-1].to_numpy() + (start_time_unix_ms/1000)
            dataArray: NDArray[float64] = df.iloc[:,i].to_numpy()
            channel_data_map[channel] = SensorNetData(channel, timeArray, dataArray)

        # channel_data_map["time"] = getTime(channel_data_map, dev_group)
        with open(pickle_filepath, "wb") as f:
            pickle.dump(channel_data_map, f, pickle.HIGHEST_PROTOCOL)
        print(
            f'conversion done!\n\n\nNext time you want to run the converter, consider calling the function with: "parseCSV(file_path_custom=\"{pickle_filepath[:-7] + ".tdms"}\")"'
        )
        return channel_data_map

def combineTDMSDatasets(existing: dict[str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]], to_add: dict[str, AnalogChannelData | DigitalChannelData | SensorNetData | list[float]]):
    if (len(existing["time"]) > len(to_add["time"])):
        to_add.update(existing)
        return to_add
    else:
        existing.update(to_add)
        return existing
