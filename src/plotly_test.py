from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from psp_liquids_daq_parser import parseTDMS, extendDatasets, parseCSV
# from matplotlib import pyplot as plt
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


# parsed_datasets: dict[
#     str,
#     AnalogChannelData | DigitalChannelData | SensorNetData | list[float],
# ] = parseTDMS(
#     5,
#     1713579651000,
#     file_path_custom="C:\\Users\\rajan\\Desktop\\PSP_Data\\sd_hotfire\\DataLog_2024-0419-2120-51_CMS_Data_Wiring_5.tdms",
# )
# parsed_datasets.update(parseTDMS(
#     6,
#     1713579651000,
#     file_path_custom="C:\\Users\\rajan\\Desktop\\PSP_Data\\sd_hotfire\\DataLog_2024-0419-2120-51_CMS_Data_Wiring_6.tdms",
# ))
thing = parseCSV(file_path_custom="C:/Users/rajan/Desktop/psp-platform/functions/test_data/timestamped_bangbang_data.csv")
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