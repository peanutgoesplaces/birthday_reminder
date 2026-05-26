

import pandas as pd
from datetime import datetime
import warnings
import smtplib
import psycopg2

warnings.simplefilter("ignore")

import os

MY_EMAIL = os.environ["MY_EMAIL"]
MY_PASSWORD = os.environ["MY_PASSWORD"]
DB_URL = os.environ['DB_URL']

today_month = datetime.today().month
today_day = datetime.today().day

def load_data():
    cur.execute("""
    SELECT first_name, last_name, month, day
    FROM birthdays
    ORDER BY month, day
    """)

    rows=cur.fetchall()

    return pd.DataFrame(rows,
                        columns=["First Name", "Last Name", "Month", "Day"]
                        )


bday_df = load_data()



message_body = ""
for _, row in bday_df.iterrows():
   if int(row['Month']) == datetime.now().month and int(row['Day']) == datetime.now().day:
        bday_rows = (
            f"{row['First Name'].title()} {row['Last Name'].title()}"

        )
        message_body += (bday_rows + "\n")
        bday_display = (
            f"{row['First Name'].title()} {row['Last Name'].title()}\n\n"

        )


if message_body != "":

    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg=f"Subject:It's Someone's Birthday!!\n\nDont Forget to Wish\n{message_body}A Happy Birthday!")





