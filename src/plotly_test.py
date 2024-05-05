import os
import pickle
from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from psp_liquids_daq_parser import parseTDMS, extendDatasets, parseCSV, combineTDMSDatasets

# from matplotlib import pyplot as plt
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

data_datasets: dict[str, list[float]] = []

# if (os.path.exists('all_channels.pickle')):
if False:
    print("unpickling expanded datasets...")
    with open("all_channels.pickle", "rb") as f:
                data_datasets = pickle.loads(f.read())
    print("unpickled expanded datasets")
else:
    file1: dict[
        str,
        AnalogChannelData | DigitalChannelData | SensorNetData | list[float],
    ] = parseTDMS(
        5,
        file_path_custom="C:\\Users\\rajan\\Desktop\\PSP_Data\\whoopsie\\DataLog_2024-0430-2328-01_CMS_Data_Wiring_5.tdms",
    )
    file2 = parseTDMS(
        6,
        file_path_custom="C:\\Users\\rajan\\Desktop\\PSP_Data\\whoopsie\\DataLog_2024-0430-2328-01_CMS_Data_Wiring_6.tdms",
    )
    parsed_datasets = combineTDMSDatasets(file1, file2)
    parsed_datasets.update(
        parseCSV(
            file_path_custom="C:/Users/rajan/Desktop/psp-platform/functions/test_data/timestamped_bangbang_data.csv"
        )
    )

    (channels, data) = extendDatasets(parsed_datasets)
    print("pickling data...")
    with open("all_channels.pickle", "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    print("pickled data")
    data_datasets = data
# sensornet_datasets = parseCSV(1713579651000,file_path_custom="C:/Users/rajan/Desktop/PSP_Data/sd_hotfire/reduced_sensornet_data.csv")

# dict_to_write: dict[str, list[float]] = {}

# all_time: list[float] = parsed_datasets["time"]

# for dataset in parsed_datasets:
dataset = "pt-ox-02"
# if dataset != "time":
# data: list[float] = parsed_datasets[dataset].data.tolist()
# time: list[float] = all_time[:len(data)]
# df = pd.DataFrame.from_dict({
#     "time": time,
#     "data": data
# })
# thing = df.iloc[::1000,:]
