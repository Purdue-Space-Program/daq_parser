from classes import SensorNetData
from psp_liquids_daq_parser import parseTDMS, extendDatasets, parseCSV
# from matplotlib import pyplot as plt
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


# channel_datasets = parseTDMS(
#     5,
#     1713579651,
#     file_path_custom="C:\\Users\\rajan\\Desktop\\PSP_Data\\sd_hotfire\\DataLog_2024-0419-2120-51_CMS_Data_Wiring_5.tdms",  # the "file_path_custom" arg is optional
# )
# channel_datasets.update(
#     parseTDMS(
#         6,
#         1713579651,
#         file_path_custom='C:\\Users\\rajan\\Desktop\\PSP_Data\\sd_hotfire\\DataLog_2024-0419-2120-51_CMS_Data_Wiring_6.tdms',
#     )
# )

# channel_datasets.update(parseTDMS(6, file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_6.tdms"))

# after combining, make all the datasets the same length by extending the datasets if necessary
# (available_tdms_channels, df_list_constant) = extendDatasets(channel_datasets)



# df_list_constant = {}
sensornet_datasets: dict[str, SensorNetData] = parseCSV(1713579651,file_path_custom="C:/Users/rajan/Desktop/PSP_Data/sd_hotfire/reduced_sensornet_data.csv")

# for channel in channel_datasets:
#     channel_object = channel_datasets[channel]
#     df_list_constant.update(
#         {channel: channel_object.data}
#     )



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

    # available_channels = ["fu_psi", "ox_psi", "sv_fu_state", "sv_ox_state"]

    # for channel in available_tdms_channels:
    #     if "reed-" in channel or "pi-" in channel:
    #         df_list.update(
    #             {
    #                 channel: df_list[channel] * binary_multiplier,
    #             }
    #         )
    # df = pd.DataFrame.from_dict(df_list)
    # fig = px.line(df, x="time", y=df.columns[0:-1]).update_traces(visible="legendonly")
    fig = go.Figure()
    for sensornet_channel in sensornet_datasets:
        fig.add_trace(go.Scatter(x=sensornet_datasets[sensornet_channel].time,y=sensornet_datasets[sensornet_channel].data, mode="lines", name=sensornet_channel))
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")
