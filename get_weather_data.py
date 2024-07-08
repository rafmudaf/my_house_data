
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta


if __name__ == "__main__":

    # Start date
    start_date = datetime(2024, 7, 3)
    # End date (today)
    end_date = datetime(2024, 7, 7)

    # Loop over the dates
    current_date = start_date

    while current_date <= end_date:

        # Cronjob to get the previous day's data
        # TARGET_DAY = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")      # Use this for a specific date outside of the while-loop
        TARGET_DAY = current_date.strftime("%Y-%m-%d")
        URL_HOST = "https://www.wunderground.com"
        PWS_ENDPOINT = "dashboard/pws"
        STROCHID = "KLANEWOR454"
        DATA_TABULAR_URL = f'{URL_HOST}/{PWS_ENDPOINT}/{STROCHID}/table/{TARGET_DAY}/{TARGET_DAY}/daily'
        response = requests.get(DATA_TABULAR_URL)
        # print(response)
        # print(response.content)

        soup = BeautifulSoup(response.content, 'html.parser')

        history_table = soup.find('table' , {'class' : 'history-table desktop-table'})
        # print(history_table.prettify())

        columns = []
        for item in history_table.find_all('th'):
            columns.append(item.get_text())
        # print(columns)

        rows = []
        for item in history_table.find_all('td'):
            rows.append(item.get_text())
        # print(rows)

        print(f"{TARGET_DAY} Number of rows: {len(rows)}")

        n_columns = len(columns)
        if len(rows) % n_columns != 0:
            raise ValueError(f'The size of the data does not match the number of columns. n_rows: {len(rows)}, n_columns: {n_columns}')

        # Make the flat list into 2d table
        n_rows = int(len(rows) / n_columns)
        rows = [rows[i*n_columns:(i+1)*n_columns] for i in range(n_rows)]
        # print(rows)

        # Remove units, ° symbol, and extra spaces
        for row in rows:
            row[1] = float(row[1].replace('°', '').replace('F', '').strip('\xa0').strip())      # Temperature
            row[2] = float(row[2].replace('°', '').replace('F', '').strip('\xa0').strip())      # Dew point
            row[3] = float(row[3].replace('°', '').replace('%', '').strip('\xa0').strip())      # Humidity
            row[4] = row[4].strip('\xa0').strip()                                               # Wind direction (string)
            row[5] = float(row[5].replace('°', '').replace('mph', '').strip('\xa0').strip())    # Wind speed
            row[6] = float(row[6].replace('°', '').replace('mph', '').strip('\xa0').strip())    # Gust
            row[7] = float(row[7].replace('°', '').replace('in', '').strip('\xa0').strip())     # Pressure (inches)
            row[8] = float(row[8].replace('°', '').replace('in', '').strip('\xa0').strip())     # Precipitation rate (inches)
            row[9] = float(row[9].replace('°', '').replace('in', '').strip('\xa0').strip())     # Precipitation accumulation (inches)
            row[10] = float(row[10].strip('\xa0').strip())                                      # UV index
            row[11] = float(row[11].replace('w/m²', '').strip('\xa0').strip())                  # Solar radiation (w/m2)
        # print(rows)

        df = pd.DataFrame(rows, columns=columns)

        # import pytz
        df["Date"] = TARGET_DAY
        time_strings = [d+" "+t for d,t in zip(df["Date"], df["Time"])]
        date_objects = [datetime.strptime(time_string, "%Y-%m-%d %I:%M %p") for time_string in time_strings]
        # date_object = date_object.replace(tzinfo=pytz.UTC)
        time_stamps = [int(date_object.timestamp() * 1e3) for date_object in date_objects]
        df["Timestamp"] = time_stamps

        # df.head()
        # df.plot(subplots=True, figsize=(10, 10))

        df.to_csv(
            'weather_data.csv',
            index=False,
            mode='a',
            header=False
        )

        # Go to the next date
        current_date += timedelta(days=1)