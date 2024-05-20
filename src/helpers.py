from datetime import datetime
import re
import time

import pytz
from classes import AnalogChannelData, DigitalChannelData
from nptdms import TdmsChannel
import numpy as np
import pandas as pd

def compileChannels(
    channels: list[TdmsChannel],
) -> tuple[dict[str, AnalogChannelData], dict[str, DigitalChannelData]]:
    toReturn_AI = {}
    toReturn_DI = {}

    for channel in channels:
        props = channel.properties
        type = props["Channel Type"]
        if "AI" in type:
            parsed_as = "AI"
            channel_data_obj = AnalogChannelData(
                rawData=channel.data,
                properties=props,
                name=props["Channel Name"],
                slope=props["Slope"],
                offset=props["Offset"],
                zeroing_target=props["Zeroing Target"],
                zeroing_correction=props["Zeroing Correction"],
                description=props["Description"],
                units=props["Unit"],
                channel_type=props["Channel Type"],
                constant_cjc=props["constant CJC"],
                tc_type=props["TC Type"],
                min_v=props["Minimum"],
                max_v=props["Maximum"],
            )
            toReturn_AI[channel_data_obj.name] = channel_data_obj
        else:
            parsed_as = "DI"
            channel_data_obj = DigitalChannelData(
                rawData=channel.data,
                properties=props,
                name=props["Channel Name"],
                channel_type=props["Channel Type"],
                description=props["Description"],
            )
            toReturn_DI[channel_data_obj.name] = channel_data_obj

        print("parsed " + channel_data_obj.name + " as " + parsed_as)
    return (toReturn_AI, toReturn_DI)


def getTime(
    channel_data: dict[str, AnalogChannelData | DigitalChannelData], group_name: str, start_time_unix_ms: int
) -> list[float]:
    samples: int = channel_data[next(iter(channel_data))].rawData.size
    pattern: str = r"\(([^()]+)\)"
    match: re.Match = re.search(pattern, group_name)
    sample_rate: float = float(match.group(1)[:-3])
    dt: float = 1 / sample_rate
    addedtime = np.arange(0, samples * dt, dt) + (start_time_unix_ms/1000)
    time: list[float] = addedtime.tolist()
    return time


def convertStringTimestamp(data, fromTimezone):
    if (str(data) == "nan"):
        return data
    test_date = data.split("+")
    thing = datetime.strptime(test_date[0], "%Y-%m-%d %H:%M:%S.%f")
    old_timezone = pytz.timezone(fromTimezone)
    new_timezone = pytz.timezone("US/Eastern")
    localized_timestamp = old_timezone.localize(thing)
    new_timezone_timestamp = localized_timestamp.astimezone(new_timezone)
    ms = new_timezone_timestamp.timestamp()
    return ms

def tdmsFilenameToSeconds(filename: str):
    time_stamp_str = filename[8:25]
    datetimeObj = datetime.strptime(time_stamp_str, "%Y-%m%d-%H%M-%S").replace(tzinfo=pytz.timezone("US/Eastern")).astimezone(pytz.utc)
    # fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
    # print(datetimeObj.strftime(fmt))
    # print(datetimeObj.timestamp())
    # dateString = time.mktime(datetimeObj.astimezone(pytz.timezone("US/Eastern")).timetuple())
    return int(datetimeObj.timestamp())

# print(tdmsFilenameToSeconds("DataLog_2024-0430-2328-01_CMS_Data_Wiring_5.tdms"))