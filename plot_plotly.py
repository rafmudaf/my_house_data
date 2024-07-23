
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import scicomap as sc

temp_colors = sc.ScicoSequential(cmap='chroma_r').get_mpl_color_map()
hum_colors = sc.ScicoSequential(cmap='chroma_r').get_mpl_color_map()
# The sequential maps have 256 colors
COLOR_GAP = 256 // 6

ROOMMAP = {
    1: "Hallway (Ref)",
    2: "Attic",
    3: "Bedroom",
    4: "Back room",
    5: "Kitchen",
    6: "Crawl space",
}

TEMPCOLORS = { i: f"rgb{tuple(temp_colors.colors[i*COLOR_GAP])}"  for i in range(1,7) }
HUMCOLORS = { i: f"rgb{tuple(hum_colors.colors[i*COLOR_GAP])}"  for i in range(1,7) }
# TEMPCOLORS = {
#     1: "#000",
#     2: "#fa6efa",
#     3: "#cd298b",
#     4: "#5c2832",
#     5: "#000",
#     6: "#000",
# }
# HUMCOLORS = {
#     1: "#000",
#     2: "#698cfd",
#     3: "#2749f5",
#     4: "#0f20c3",
#     5: "#000",
#     6: "#000",
# }
BATTCOLORS = {
    1: "#000",
    2: "#b8b8b8",
    3: "#767676",
    4: "#3c3c3c",
    5: "#000",
    6: "#000",
}

N_SENSORS = len(ROOMMAP)

TIMEZONE = "US/Central"     # Data is in UTC, this sets the timezone to display the data on the dashboard
# TIME_FMT = "%b %d, %y %I:%M p"
# TIME_FMT = "%d/%m/%Y"

df = pd.read_csv("sensor_data.csv")
df["Date"] = pd.to_datetime(
    df["timestamp"],
    unit="ms",
    utc=True,
    # format=TIME_FMT
).dt.tz_convert(tz=TIMEZONE)
for i in range(1,N_SENSORS+1):
    # Convert temperature from Celsius to Fahrenheit
    df[f"temp{i}"] = df[f"temp{i}"] / 10.0
    df[f"temp{i}"] = df[f"temp{i}"] * (9.0/5.0) + 32

    # Humidity are multiplied by 10 and stored as ints on the sensor
    df[f"hum{i}"] = df[f"hum{i}"] / 10.0

weather_df = pd.read_csv("weather_data.csv")
weather_df["Date"] = pd.to_datetime(
    weather_df["Timestamp"],
    unit="ms",
    utc=True,
    # format=TIME_FMT
).dt.tz_convert(tz=TIMEZONE)

fig = make_subplots(
    rows=3,
    cols=1,
    vertical_spacing=0.065,
    shared_xaxes=True,
    specs=[
        [{"secondary_y": True}],
        [{"secondary_y": False}],
        [{"secondary_y": False}]
    ]
)
# print(fig.layout)

# Temperature plot
fig.add_trace(
    go.Scatter(
        x=list(weather_df.Date),
        y=list(weather_df["Temperature"]),
        name=f"St Roch Temperature",
        legend="legend",
        line=dict(
            color="#000",
            width=1.0,
            dash="dash"
        )
    ),
    1,
    1,
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=list(weather_df.Date),
        y=list(weather_df["Solar"]),
        name=f"St Roch Solar Radiance",
        legend="legend",
        line=dict(
            color="#000",
            width=1.0,
            dash="dot"
        )
    ),
    1,
    1,
    secondary_y=True
)
for i in range(1,N_SENSORS+1):
    fig.add_trace(
        go.Scatter(
            x=list(df.Date),
            y=list(df[f"temp{i}"]),
            name=f"{ROOMMAP[i]}",
            line_color=TEMPCOLORS[i],
        ),
        1,
        1,
        secondary_y=False,
    )
fig.add_annotation(
    xref="x domain",
    yref="y domain",
    x=0.5,
    y=1.1,
    showarrow=False,
    text="Temperature",
    row=1,
    col=1
)

# Humidity plot
fig.add_trace(
    go.Scatter(
        x=list(weather_df.Date),
        y=list(weather_df["Humidity"]),
        name=f"St Roch Humidity",
        line=dict(
            color="#000",
            width=1.0,
            dash="dot"
        )
    ),
    2,
    1
)
for i in range(1,N_SENSORS+1):
    fig.add_trace(
        go.Scatter(
            x=list(df.Date),
            y=list(df[f"hum{i}"]),
            name=f"{ROOMMAP[i]}",
            line_color=HUMCOLORS[i],
        ),
        2,
        1
    )
fig.add_annotation(
    xref="x domain",
    yref="y domain",
    x=0.5,
    y=1.1,
    showarrow=False,
    text="Humidity",
    row=2,
    col=1
)

# Battery plot
for i in range(1,N_SENSORS+1):
    fig.add_trace(
        go.Scatter(
            x=list(df.Date),
            y=list(df[f"batt{i}"]),
            name=f"{ROOMMAP[i]}",
            line_color=BATTCOLORS[i],
        ),
        3,
        1
    )
fig.add_annotation(
    xref="x domain",
    yref="y domain",
    x=0.5,
    y=1.1,
    showarrow=False,
    text="Battery Level",
    row=3,
    col=1
)

# Main layout
fig.update_layout(
    title_text="Temperature and Humidity",
    xaxis=dict(
        rangeselector={
            "buttons": [
                {
                    "count": 1,
                    "label": "1h",
                    "step": "hour",
                    "stepmode": "backward"
                },
                {
                    "count": 1,
                    "label": "1d",
                    "step": "day",
                    "stepmode": "backward"
                },
                {
                    "count": 7,
                    "label": "1w",
                    "step": "day",
                    "stepmode": "backward"
                },
                {
                    "count": 1,
                    "label": "1m",
                    "step": "month",
                    "stepmode": "backward"
                },
                {
                    "count": 6,
                    "label": "6m",
                    "step": "month",
                    "stepmode": "backward"
                },
                {
                    "count": 1,
                    "label": "1y",
                    "step": "year",
                    "stepmode": "backward",
                },
                {
                    "step": "all"
                }
            ]
        },
        type="date"
    ),
    # xaxis3_rangeslider_visible=True,
    # xaxis3_type="date"
)

fig.write_html("docs/index.html")
# fig.show()
