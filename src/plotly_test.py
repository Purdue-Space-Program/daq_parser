from psp_liquids_daq_parser import parseTDMS, extendDatasets, parseCSV
# from matplotlib import pyplot as plt
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


# channel_datasets = parseTDMS(
#     5,
#     file_path_custom="C:/Users/rajan/Desktop/PSP_Data/cf2/DataLog_2024-0406-1735-43_CMS_Data_Wiring_5.tdms",
# )
# channel_datasets.update(parseTDMS(
#     6,
#     file_path_custom="C:/Users/rajan/Desktop/PSP_Data/cf2/DataLog_2024-0406-1735-43_CMS_Data_Wiring_6.tdms",
# ))

# channel_datasets.update(parseTDMS(6, file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_6.tdms"))

# after combining, make all the datasets the same length by extending the datasets if necessary
# (available_channels, df_list_constant) = extendDatasets(channel_datasets)


channel_datasets = parseCSV(file_path_custom="C:/Users/rajan/Desktop/PSP_Data/sd_hotfire/reduced_sensornet_data.csv")

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            children="Short Duration Hotfire Data",
            style={"textAlign": "center", "fontFamily": "sans-serif"},
        ),
        html.I("scale PI/binary data by: "),
        dcc.Input(
            id="input_{}".format("number"),
            type="number",
            placeholder="input type {}".format("number"),
            debounce=True,
            value=5000,
        ),
        dcc.Graph(id="graph-content", style={"width": "95vw", "height": "85vh"}),
    ]
)


# This is called whenver input is submitted (usually by the user clicking out of the input box), and re-draws the UI
@callback(Output("graph-content", "figure"), Input("input_number", "value"))
def update_graph(value):
    binary_multiplier: float = float(value)
    # print(available_channels)
    df_list = {}
    # df_list.update(df_list_constant)

    # for channel in available_channels:
    #     if "reed-" in channel or "pi-" in channel:
    #         df_list.update(
    #             {
    #                 channel: df_list[channel] * binary_multiplier,
    #             }
    #         )
    df = pd.DataFrame.from_dict(df_list)
    fig = px.line(df, x="time", y=df.columns[0:-1])
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")
