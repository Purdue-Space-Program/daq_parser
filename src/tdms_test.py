from nptdms import TdmsFile, TdmsGroup
import re

with TdmsFile.open("./src/DataLog_2021-1107-1622-03_BZB_Data_Wiring_5.tdms") as tdms_file:

    all_groups = tdms_file.groups()
    first: TdmsGroup = all_groups[0]
    print(first)
    pattern: str = r"\(([^()]+)\)"
    match: re.Match = re.search(pattern, first.name)
    sample_rate: float = float(match.group(1)[:-3])
    print(sample_rate)
