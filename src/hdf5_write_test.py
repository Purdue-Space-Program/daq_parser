from datetime import datetime, timedelta
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
# import gdown
import os
import time as t
import h5py
import numpy as np
import pandas as pd
import time

import pytz
from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from psp_liquids_daq_parser import (
    combineTDMSDatasets,
    extendDatasets,
    parseCSV,
    parseTDMS,
)
import matplotlib.pyplot as plt


def organizeFiles(file_names: list[str]):
    csv_files = list(filter(lambda x: ".csv" in x, file_names))
    fileNames = list(filter(lambda x: ".csv" not in x, file_names))
    fileNames.sort()
    timestamps: list[int] = []
    for file in fileNames:
        time_stamp_str = file[8:25]
        datetimeObj = datetime.strptime(time_stamp_str, "%Y-%m%d-%H%M-%S")
        dateString = t.mktime(datetimeObj.timetuple())
        timestamps.append(int(dateString))
    return (fileNames, csv_files, timestamps)


# def downloadFromGDrive(url: str):
#     print("new download: " + url)
#     file_name = gdown.download(url=url, fuzzy=True)
#     return file_name


def getUnits(dataset_name: str) -> str:
    scale = "psi"
    if "tc" in dataset_name:
        scale = "deg"
    if "pi-" in dataset_name or "reed-" in dataset_name or "_state" in dataset_name:
        scale = "bin"
    if "fms" in dataset_name:
        scale = "lbf"
    if "rtd" in dataset_name:
        scale = "V"
    return scale


def run():
    file_names = [
        "DataLog_2024-0430-2328-01_CMS_Data_Wiring_5.tdms",
        "DataLog_2024-0430-2328-01_CMS_Data_Wiring_6.tdms",
        "DataLog_2024-0501-0002-02_CMS_Data_Wiring_5.tdms",
        "DataLog_2024-0501-0002-02_CMS_Data_Wiring_6.tdms",
        # "DataLog_2024-0501-0031-41_CMS_Data_Wiring_5.tdms",
        # "DataLog_2024-0501-0031-41_CMS_Data_Wiring_6.tdms",
        "timestamped_bangbang_data.csv",
    ]
    print("downloading...")
    # cpus = cpu_count()
    # results = ThreadPool(cpus - 1).imap_unordered(downloadFromGDrive, url_pairs)
    # for result in results:
    #     file_names.append(result)
    #     print("downloaded:", result)
    (tdms_filenames, csv_filenames, starting_timestamps) = organizeFiles(file_names)

    postProcessingTimeStart = time.time()

    masterDF = pd.DataFrame.from_dict({"time": []})

    for tdmsFile in tdms_filenames:
        fileData = parseTDMS(0, file_path_custom=tdmsFile)
        print(os.path.getsize(tdmsFile))
        updatedColumnNames = {"time": (np.array(fileData["time"]) * 1000) + 8327}
        print(tdmsFile)
        for dataset in fileData:
            if dataset != "time":
                updatedColumnNames[f"{dataset}__{getUnits(dataset)}__"] = fileData[
                    dataset
                ].data.tolist()
                print(len(updatedColumnNames[f"{dataset}__{getUnits(dataset)}__"]))
        df = pd.DataFrame.from_dict(updatedColumnNames)
        df = df.dropna(subset=["time"])
        if masterDF.empty:
            masterDF = df
        else:
            masterDF = (
                masterDF.merge(
                    df,
                    how="outer",
                    on="time",
                    suffixes=["---merge---x", "---merge---y"],
                )
                .T.groupby(lambda x: x.split("---merge---")[0])
                .last()
                .T
            )

    for csvFile in csv_filenames:
        csvData = parseCSV(file_path_custom=csvFile)
        for datasetName in csvData:
            dataset = csvData[datasetName]
            df = pd.DataFrame.from_dict(
                {
                    "time": np.rint(dataset.time * 1000),
                    f"{datasetName}__{getUnits(datasetName)}__": dataset.data.tolist(),
                }
            )
            df = df.dropna(subset=["time"])
            if masterDF.empty:
                masterDF = df
            else:
                masterDF = masterDF.merge(df, how="outer", on="time", copy=False)

    masterDF = masterDF.ffill().bfill()

    masterDF["time"] = masterDF["time"].round()
    masterDF["time"] = masterDF["time"].astype("Int64")
    masterDF = masterDF.sort_values("time")

    # plt.plot(masterDF["time"], masterDF["fu_psi__psi__"])
    # plt.plot(masterDF["time"], masterDF["pi-fu-02__bin__"])
    # plt.show()

    writeTimeStart = time.time()
    with h5py.File("zggWCpa.hdf5", "w") as f:
        cols = masterDF.columns.tolist()
        openFileTime = time.time()
        for col in cols:
            startTime = time.time()
            dset = f.create_dataset(col, data=masterDF[col])
            endTime = time.time()
            print(f"Wrote {dset.name} in {(endTime - startTime)*1000} ms")
    writeTimeEnd = time.time()
    print(
        f"Post-processed data in {(writeTimeStart - postProcessingTimeStart)*1000} ms"
    )
    print(f"Opened file in {(openFileTime - writeTimeStart)*1000} ms")
    print(f"Wrote file in {(writeTimeEnd - writeTimeStart)*1000} ms")
    return "done"


print(run())
