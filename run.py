# -*- coding: utf-8 -*-
# Copyright (c) 2019 Linh Pham
# wwdtm_uniquedates is relased under the terms of the Apache License 2.0
"""Calculates all of the calendar days for each month in which there has been
a Wait Wait Don't Tell Me! show"""

from collections import OrderedDict
import json
import math
import os
import textwrap
from typing import List, Dict
import mysql.connector

MONTHS = ["January", "February", "March", "April",
          "May", "June", "July", "August",
          "September", "October", "November", "December"
          ]

MONTH_NUMBER_OF_DAYS = [31, 29, 31, 30,
                        31, 30, 31, 31,
                        30, 31, 30, 31
                        ]

def retrieve_all_shows(database_connection: mysql.connector.connect,
                       max_year: int = 2020) -> Dict:
    """..."""
    all_show_dates = OrderedDict()
    regular_show_dates = OrderedDict()

    for month in range(1, 13, 1):
        all_show_dates[month] = []
        regular_show_dates[month] = []

    cursor = database_connection.cursor(dictionary=True)
    query = ("SELECT s.showdate, s.bestof, s.repeatshowid FROM ww_shows s "
             "WHERE YEAR(s.showdate) <= %s "
             "ORDER BY s.showdate ASC;")
    cursor.execute(query, (max_year,))
    result = cursor.fetchall()

    if not result:
        return None

    for show in result:
        show_date = show["showdate"]

        if show_date.day not in all_show_dates[show_date.month]:
            all_show_dates[show_date.month].append(show_date.day)

        if not show["bestof"] and not show["repeatshowid"]:
            if show_date.day not in regular_show_dates[show_date.month]:
                regular_show_dates[show_date.month].append(show_date.day)

    for month in all_show_dates:
        all_show_dates[month].sort()

    for month in regular_show_dates:
        regular_show_dates[month].sort()

    return all_show_dates, regular_show_dates

def load_config(app_environment) -> Dict:
    """Load configuration file from config.json"""
    with open('config.json', 'r') as config_file:
        config_dict = json.load(config_file)

    return config_dict

def main():
    """Pull in scoring data and generate stats based on the data"""
    app_environment = os.getenv("APP_ENV", "local").strip().lower()
    config = load_config(app_environment)
    database_connection = mysql.connector.connect(**config["database"])
    all_show_dates, regular_show_dates = retrieve_all_shows(database_connection)

    print("All Shows")
    print("=========\n")
    for month in all_show_dates:
        print(MONTHS[month - 1])
        print("")
        days = " ".join("{:<3}".format(day) for day in all_show_dates[month])
        for line in textwrap.wrap(days, 30):
            print(line)

        print("")
        print("Days in {}: {}".format(MONTHS[month - 1],
                                      MONTH_NUMBER_OF_DAYS[month - 1]))
        print("Show days in {}: {}\n".format(MONTHS[month -1],
                                             len(all_show_dates[month])))

    print("")
    print("Regular Shows")
    print("=============\n")
    for month in regular_show_dates:
        print(MONTHS[month - 1])
        print("")
        days = " ".join("{:<3}".format(day) for day in regular_show_dates[month])
        for line in textwrap.wrap(days, 30):
            print(line)

        print("")
        print("Days in {}: {}".format(MONTHS[month - 1],
                                      MONTH_NUMBER_OF_DAYS[month - 1]))
        print("Show days in {}: {}\n".format(MONTHS[month -1],
                                             len(regular_show_dates[month])))


    return None

# Only run if executed as a script and not imported
if __name__ == "__main__":
    main()
