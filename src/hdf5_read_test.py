import h5py
import time
import pandas as pd
import math
import statistics

import matplotlib.pyplot as plt
# searchStart = 0
# searchEnd = 39823
# searchStart = 1714537441001
# searchEnd = 1714537443817
# channel_to_fetch = ["fms__lbf__", "pi-fu-02__bin__", "fu_psi__psi__"]
# maxVals = 4500

# totalStartTime = time.time()
# df = pd.DataFrame()
# avgPerfTime = []

with h5py.File("Kh8celn.hdf5", "r") as f:
    # channel_to_fetch.append("time")
    # datasets = list(f.keys())
    # print(datasets)
    print(f["time"][:])
    # plt.plot(f["time"][:], f["fu_psi__psi__"][:])
    plt.plot(f["time"][:], f["fms__lbf__"][:])
    plt.show()
    # for dataset in channel_to_fetch:
    #     startTime = time.time()
    #     dset = f[dataset]
    #     endTime = time.time()
    #     avgPerfTime.append((endTime - startTime)*1000)
    #     df[dataset] = dset


# print(f'Avg fetch time per channel: {statistics.fmean(avgPerfTime)} ms')

# fetchEndTime = time.time()
# totalLength = len(df.index)
# nth = math.ceil(totalLength / maxVals)
# print(nth)

# downsampledDF = df.iloc[1::nth]

# filteredDF = df.iloc[1::nth].loc[(df['time'] >= searchStart) & (df.iloc[1::nth]['time'] <= searchEnd)]

# totalEndTime = time.time()
# print(f'Fetched all data in {(fetchEndTime - totalStartTime)*1000} ms')
# print(f'downsampled and filtered in {(totalEndTime - fetchEndTime)*1000} ms')
# print(filteredDF)

# print("done")

