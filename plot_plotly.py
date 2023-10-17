
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

ROOMMAP = {
    1: "Hallway (Ref)",
    2: "Kitchen",
    3: "Bedroom",
    4: "Back room",
}
TEMPCOLORS = {
    1: "#000",
    2: "#fa6efa",
    3: "#cd298b",
    4: "#5c2832",
}

HUMCOLORS = {
    1: "#000",
    2: "#698cfd",
    3: "#2749f5",
    4: "#0f20c3",
}

df = pd.read_csv("datapoints.csv")
df["Date"] = pd.to_datetime(df["timestamp"]/1e3, unit="s")
for i in range(1,5):
    # Convert temperature from Celsius to Fahrenheit
    df[f"temp{i}"] = df[f"temp{i}"] / 10.0
    df[f"temp{i}"] = df[f"temp{i}"] * (9.0/5.0) + 32

    # Humidity are multiplied by 10 and stored as ints on the sensor
    df[f"hum{i}"] = df[f"hum{i}"] / 10.0


fig = make_subplots(
    rows=2,
    cols=1,
    vertical_spacing=0.065,
    shared_xaxes=True
)

for i in range(1,5):
    fig.add_trace(
        go.Scatter(
            x=list(df.Date),
            y=list(df[f"temp{i}"]),
            # visible="legendonly"
            name=f"Temp {ROOMMAP[i]}",
            line_color=TEMPCOLORS[i]
        ),
        1,
        1
    )

for i in range(1,5):
    fig.add_trace(
        go.Scatter(
            x=list(df.Date),
            y=list(df[f"hum{i}"]),
            # visible="legendonly"
            name=f"Hum {ROOMMAP[i]}",
            line_color=HUMCOLORS[i]
        ),
        2,
        1
    )

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
    xaxis2_rangeslider_visible=True,
    xaxis2_type="date"
)

fig.write_html("docs/index.html")
# fig.show()
