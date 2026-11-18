import tkinter

import pandas as pd
from datetime import datetime
import warnings
from tkinter import *
from tkinter import ttk
#import smtplib
import psycopg2
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

MY_EMAIL = os.environ["MY_EMAIL"]
MY_PASSWORD = os.environ["MY_PASSWORD"]
DB_URL = os.environ["DB_URL"]


# Connect to Railway
conn = psycopg2.connect(os.environ["DATABASE_PUBLIC_URL"])


cur = conn.cursor()

warnings.simplefilter("ignore")

# Creates DataFrame from SQL Database
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


#________________________________________________
MY_EMAIL = "DouglasSchwartz11@gmail.com"
MY_PASSWORD = "xdaj kbls aarv gmrt"


today_month = datetime.today().month
today_day = datetime.today().day

window = Tk()
window.configure(background="white", padx=5, pady=5)
window.minsize(600, 500)
window.title("Birthday Wisher")

# Print Box For All Listed Birthdays
print_box = Text(window, background="white",
                 height=10, width=50)
print_box.grid(row=0, column=0, columnspan=3, padx=75, pady=10)
print_box.insert(END, bday_df.to_string(index=False, header=True))

first_name_input = Entry(window, width=30, bd=1, relief="solid")
first_name_input.insert(END, "First Name")
first_name_input.grid(row=2, column=0, columnspan=2, pady=20)

last_name_input = Entry(window, width=30, bd=1, relief="solid")
last_name_input.insert(END, "Last Name")
last_name_input.grid(row=3, column=0, columnspan=2, pady=20)

bday_input = Entry(window, width=30, bd=1, relief="solid")
bday_input.insert(END, "Birthday: May 03 2020")
bday_input.grid(row=4, column=0, columnspan=2, pady=20)

# bday_box is Where Added Names are Displayed and Current Birthdays Displayed
bday_box = Text(window, background="white", height=9, width=22)
bday_box.place(x=300, y=200)

def clear_entry(event):
    event.widget.delete(0, END)


first_name_input.bind("<FocusIn>", clear_entry)
last_name_input.bind("<FocusIn>", clear_entry)
bday_input.bind("<FocusIn>", clear_entry)

#Removes Entry from Print Box and DataBase
def delete_entry(tree):
    global bday_df
    selected = tree.selection()
    for item in selected:
        values = tree.item(item, "values")
        first_name = values[0]
        last_name = values[1]
        month = values[2].split("-")[0]
        day = values[2].split("-")[1]

        cur.execute("""
            DELETE FROM public.birthdays
            WHERE first_name = %s AND last_name = %s AND month= %s AND day = %s
            """,
                    (first_name, last_name, month, day)
        )

        conn.commit()

    tree.delete(item)
    update_print_box()


#Creates Window That Allows for Removal of Entry
def remove_entry():
    popup=Toplevel(window)
    popup.title("Remove Entry")
    popup.geometry("400x325")

    table_frame=Frame(popup)
    table_frame.pack(fill="both", expand=True)
    table_frame.config(padx=25, pady=25)
    tree = ttk.Treeview(table_frame, columns=("First Name", "Last Name", "Birthday"),
                        show="headings")
    separator = ttk.Separator(table_frame, orient="horizontal")
    separator.pack(fill="x")

    tree.heading("First Name", text="First Name")
    tree.heading("Last Name", text="Last Name")
    tree.heading("Birthday", text="Birthday")

    tree.column("First Name", width=100)
    tree.column("Last Name", width=100)
    tree.column("Birthday", width=100)

    #Displays List of Names in Birthday DF
    for _, row in bday_df.iterrows():
        bday_display_date = f"{int(row['Month']):02d}-{int(row['Day']):02d}"
        tree.insert("", "end", values=(
                    row['First Name'],
                    row['Last Name'],
                    bday_display_date
                    )
                    )

    button_frame=Frame(popup)
    button_frame.pack(fill="both", expand=True)

    delete_button = Button(button_frame, text="Remove Entry", command=lambda: delete_entry(tree))
    delete_button.pack(anchor=CENTER, padx=5, pady=5)


    tree.pack(fill="both")

remove_button = Button(text="Remove", command=remove_entry)
remove_button.place(x=490, y=85)
#________________________________________________________________________
def update_bday_box():
    bday_box.delete("1.0", END)
    bday_box.insert(END, "Happy Birthday\n\n", "big")
    bday_box.tag_configure("big", font=("Times New Roman", 14), justify="center")
    bday_box.insert(END, bday_display)

# Updates Print Box when New Names are Added
def update_print_box():
    global bday_df
    global df

    cur.execute("""
        SELECT first_name, last_name, month, day
        FROM public.birthdays
        ORDER BY month, day
        """)

    rows = cur.fetchall()

    bday_df = pd.DataFrame(rows, columns=['First Name', 'Last Name', 'Month', 'Day'] )
    print_box.delete("1.0", END)

    print_box.insert(END, bday_df.to_string(index=False, header=True))

# Adds New Birthday Entry
def add_bday():
    global bday_copy
    global bday_df
    f_name_input = first_name_input.get().lower().title()
    l_name_input = last_name_input.get().lower().title()
    date_input = bday_input.get().lower().title()
    while True:
        try:
            date = datetime.strptime(date_input, "%B %d %Y")
            break

        except ValueError:
            bday_box.delete("2.0", END)
            bday_box.insert("2.0", "\n\nInvalid Date\nTry Again")
            return

    conn.rollback()

    cur.execute("""
    INSERT INTO public.birthdays (first_name, last_name, month, day)
    VALUES (%s, %s,%s, %s)
    """, (f_name_input, l_name_input, date.month, date.day)
                )

    conn.commit()
    bday_df = load_data()
    bday_box.delete("1.0", END)
    bday_box.insert(END, "Happy Birthday\n\n", "big")
    bday_box.tag_configure("big", font=("Times New Roman", 14), justify="center")
    for _, row in bday_df.iterrows():
        if int(row['Month']) == datetime.now().month and int(row['Day']) == datetime.now().day:
            bday_display = (
                f"{row['First Name'].title()} {row['Last Name'].title()}\n\n"
            )

            bday_box.insert(END, bday_display)

    update_print_box()


balloons = PhotoImage(file="C:/Users/dougl/PycharmProjects/bday_email/Birthday Wisher (Day 32) start/balloons_small.png")
add_button = Button(window, image=balloons, borderwidth=0, command=add_bday, bg="white")
add_button.image = balloons
add_button.grid(row=5, column=0, columnspan=2, pady=15, sticky=N, rowspan=2)

bday_box.insert(END, "Happy Birthday\n\n", "big")
bday_box.tag_configure("big", font=("Times New Roman", 14), justify="center")

# Creates Message for Email
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

        bday_box.insert(END, bday_display)

#__________________________________________________________________________
# if message_body != "":
#
#     with smtplib.SMTP('smtp.gmail.com', 587) as connection:
#         connection.starttls()
#         connection.login(user=MY_EMAIL, password=MY_PASSWORD)
#         connection.sendmail(from_addr=MY_EMAIL,
#                             to_addrs=MY_EMAIL,
#                             msg=f"Subject:It's Someone's Birthday!!\n\nDont Forget to Wish\n{message_body}A Happy Birthday!")

#_________________________________________________________________________________

if message_body != "":

    token_data = json.loads(os.environ["GMAIL_TOKEN"])

    credentials = Credentials.from_authorized_user_info(
        token_data,
        ["https://www.googleapis.com/auth/gmail.send"]
    )

    service = build("gmail", "v1", credentials=credentials)

    email_message = MIMEText(
        f"Don't Forget to Wish\n{message_body}A Happy Birthday!"
    )

    email_message["to"] = MY_EMAIL
    email_message["from"] = MY_EMAIL
    email_message["subject"] = "It's Someone's Birthday!!"

    encoded_message = base64.urlsafe_b64encode(
        email_message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    print("Birthday email sent successfully!")



window.mainloop()
