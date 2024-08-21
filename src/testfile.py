from datetime import datetime
import decimal
import logging
import math
import sys
# from multiprocessing import cpu_count
# from multiprocessing.pool import ThreadPool
# import pickle
from botocore.exceptions import ClientError
import boto3
import time as t

import pandas as pd

from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from psp_liquids_daq_parser import (
    combineTDMSDatasets,
    extendDatasets,
    parseCSV,
    parseTDMS,
)

s3 = boto3.client("s3")


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


def run():
    test_name: str = "Whoopsie"
    test_id: str = "test_run_all"
    test_article: str = "CMS"
    gse_article: str = "BCLS"
    trim_to_s: int = 0
    max_entries_per_sensor: int = 4500
    # url_pairs: list[str] = [
    #     "https://drive.google.com/file/d/10M68NfEW9jlU1XMyv5ubRzIoKsWTQ_MY/view?usp=drive_link",
    #     "https://drive.google.com/file/d/1SKDAxE1udwTQtjbmGNZapU4nRv1hGNZT/view?usp=drive_link",
    #     "https://drive.google.com/file/d/1zoMto1MpyK6P62iSg0Jz-AfUzmVBy5ZE/view?usp=drive_link",
    # ]
    file_names = [
        "DataLog_2024-0430-2328-01_CMS_Data_Wiring_5.tdms",
        "DataLog_2024-0430-2328-01_CMS_Data_Wiring_6.tdms",
        "timestamped_bangbang_data.csv",
    ]
    # file_names: list[str] = []

    print("downloading...")
    # cpus = cpu_count()
    # results = ThreadPool(cpus - 1).imap_unordered(downloadFromGDrive, url_pairs)
    # for result in results:
    #     file_names.append(result)
    #     print("downloaded:", result)
    (tdms_filenames, csv_filenames, starting_timestamps) = organizeFiles(file_names)
    parsed_datasets: dict[
        str,
        AnalogChannelData | DigitalChannelData | SensorNetData | list[float],
    ] = []
    file1 = parseTDMS(0, file_path_custom=tdms_filenames[-1])
    file2 = parseTDMS(0, file_path_custom=tdms_filenames[-2])
    parsed_datasets = combineTDMSDatasets(file1, file2)
    # parsed_datasets.update(parseCSV(file_path_custom=csv_filenames[-1]))
    [channels, max_length, data_as_dict] = extendDatasets(parsed_datasets)
    # [channels, max_length, data_as_dict] = extendDatasets(file1)
    df = pd.DataFrame.from_dict(data_as_dict)
    available_datasets: list[str] = []
    for dataset in data_as_dict:
        if dataset != "time":
            scale = "psi"
            if "tc" in dataset:
                scale = "deg"
            if "pi-" in dataset or "reed-" in dataset or "_state" in dataset:
                scale = "bin"
            if "fms" in dataset:
                scale = "lbf"
            if "rtd" in dataset:
                scale = "V"
            df2 = df.rename(columns={f'{dataset}':f'{dataset}__{scale}__'})
            df = df2
            available_datasets.append(dataset)
    df["measure_name"] = test_id
    # df["test_name"] = test_name
    # df["test_article"] = test_article
    # df["gse_article"] = gse_article
    df['time'] = df['time'].apply(lambda x: x*1000)
    df['time'] = df['time'].round()
    df['time'] = df['time'].astype('Int64')
    cols = df.columns.tolist()
    cols = [cols[0]] + cols[-4:] + cols[1:-4]
    df = df[cols]
    df.to_csv(f'{test_id}.csv', sep=",", index=False)
    try:
        response = s3.upload_file(f'{test_id}.csv', "psp-data-viewer", f'all_data/{test_id}.csv')
    except ClientError as e:
        logging.error(e)
    return {"name": test_name, "id": test_id, "response": response}


print(run())
