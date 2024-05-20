from datetime import datetime
import math
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import pickle
import time

import pandas as pd

from classes import AnalogChannelData, DigitalChannelData, SensorNetData
from psp_liquids_daq_parser import (
    combineTDMSDatasets,
    extendDatasets,
    parseCSV,
    parseTDMS,
)


def organizeFiles(file_names: list[str]):
    csv_files = list(filter(lambda x: ".csv" in x, file_names))
    fileNames = list(filter(lambda x: ".csv" not in x, file_names))
    fileNames.sort()
    timestamps: list[int] = []
    for file in fileNames:
        time_stamp_str = file[8:25]
        datetimeObj = datetime.strptime(time_stamp_str, "%Y-%m%d-%H%M-%S")
        dateString = time.mktime(datetimeObj.timetuple())
        timestamps.append(int(dateString))
    return (fileNames, csv_files, timestamps)


# def downloadFromGDrive(url: str):
#     print("new download: " + url)
#     file_name = gdown.download(url=url, fuzzy=True)
#     return file_name


def run():
    test_name: str = "Name"
    test_id: str = "ID"
    test_article: str = "CMS"
    gse_article: str = "BCLS"
    trim_to_s: int = 10
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
    parsed_datasets.update(parseCSV(file_path_custom=csv_filenames[-1]))
    [channels, max_length, data_as_dict] = extendDatasets(parsed_datasets)
    # print("pickling data...")
    # with open("test_data/all_channels.pickle", "wb") as f:
    #     pickle.dump(data_as_dict, f, pickle.HIGHEST_PROTOCOL)
    # print("pickled data")
    # file_names.append("test_data/all_channels.pickle")

    # db = firestore.client()
    all_time: list[float] = data_as_dict["time"]
    available_datasets: list[str] = []
    for dataset in data_as_dict:
        if dataset != "time":
            data: list[float] = data_as_dict[dataset]
            time: list[float] = all_time[: len(data)]
            df = pd.DataFrame.from_dict({"time": time, "data": data})
            if trim_to_s == 0:
                print("not trimming")
                processed_df = df.iloc[:: math.ceil(max_length / max_entries_per_sensor), :]
            else:
                df_cut = df.head(trim_to_s * 1000)
                max_length = len(df_cut.index)
                trim_to_freq = math.ceil(max_length / max_entries_per_sensor)
                print("Trimming to every x samples: " + str(trim_to_freq))
                processed_df = df_cut.iloc[::trim_to_freq, :]
            scale = "psi"
            if "tc" in dataset:
                scale = "deg"
            if "pi-" in dataset or "reed-" in dataset or "_state" in dataset:
                scale = "bin"
            if "fms" in dataset:
                scale = "lbf"
            if "rtd" in dataset:
                scale = "V"
            # doc_ref = db.collection(test_id).document(dataset)
            # doc_ref.set({"time_offset": (time[0])})
            # doc_ref.set(
            #     {
            #         "data": thing["data"].to_list(),
            #         "time": thing["time"].to_list(),
            #         "unit": scale,
            #     },
            #     merge=True,
            # )
            available_datasets.append(dataset)
            print(dataset)

    # doc_ref_test_general = db.collection(test_id).document("general")
    # doc_ref_test_general.set(
    #     {
    #         "datasets": available_datasets,
    #         "test_article": test_article,
    #         "gse_article": gse_article,
    #         "name": test_name,
    #     },
    #     merge=True,
    # )
    # general_doc_ref = db.collection("general").document("tests")
    # general_doc_ref.update(
    #     {
    #         "visible": fs.ArrayUnion(
    #             [
    #                 {
    #                     "id": test_id,
    #                     "test_article": test_article,
    #                     "gse_article": gse_article,
    #                     "name": test_name,
    #                 }
    #             ]
    #         )
    #     }
    # )

    # storage_client = storage.Client()
    # bucket = storage_client.bucket("psp-data-viewer-storage")
    # print("uploading...")
    # results = transfer_manager.upload_many_from_filenames(
    #     bucket,
    #     file_names,
    #     blob_name_prefix=test_id + "/",
    #     source_directory=".",
    #     max_workers=6,
    # )
    # for name, result in zip(file_names, results):
    #     # The results list is either `None` or an exception for each filename in
    #     # the input list, in order.
    #     if isinstance(result, Exception):
    #         print("Failed to upload {} due to exception: {}".format(name, result))
    #     else:
    #         print("Uploaded {} to {}.".format(name, bucket.name))
    return {"name": test_name, "id": test_id}


run()