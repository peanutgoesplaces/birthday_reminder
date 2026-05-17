

import pandas as pd
from datetime import datetime
import warnings
import smtplib

warnings.simplefilter("ignore")

MY_EMAIL = "DouglasSchwartz11@gmail.com"
MY_PASSWORD = "xdaj kbls aarv gmrt"



bday_df = pd.read_csv("bday.csv")


today_month = datetime.today().month
today_day = datetime.today().day



message_body = ""
for _, row in bday_df.iterrows():
   if int(row['Birthday'].split("-")[0]) == datetime.now().month and int(row['Birthday'].split("-")[1]) == datetime.now().day:
        bday_rows = (
            f"{row['First Name'].title()} {row['Last Name'].title()}"

        )
        message_body += (bday_rows + "\n")


if message_body != "":

    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg=f"Subject:It's Someone's Birthday!!\n\nDont Forget to Wish\n{message_body}A Happy Birthday!")

