#!/usr/bin/env python
##
# Author: Fred Faloona
# epoch: Pandemic years

import matplotlib.pyplot as plt

import pandas
import numpy as np
from datetime import datetime, timedelta

import requests
import os
import click

DIFF_WINDOW = 7

covidcnts_file="/Users/fredafal/Downloads/COVID-19_aantallen_gemeente_cumulatief.csv"
Municipality = "Leiden"
        
def download_covid_nums():
    url = 'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv'
    # may want to find size and take last part
    # fsize = int(requests.get(url, stream=True).headers['Content-length'])
    # bytes_to_get = 1000000
    # begin = str(fsize - bytes_to_get)
    # end = str(fsize)
    # range_s = f'bytes={begin}-{fsize}'
    # r = requests.get(url, headers= {"range": range_s })
    r = requests.get(url, allow_redirects=True)
    f = open(covidcnts_file, 'wb')
    f.write(r.content)
    f.close()
    
    
def get_covid_df_days(df,days):
    now = datetime.now()
    dtnow_str = now.strftime("%Y-%m-%d") + " 10:00:00"
    beg_date = now - timedelta(days=days)
    dtbeg_str = beg_date.strftime("%Y-%m-%d") + " 10:00:00"

    dfwindow = df[(df['Date_of_report'] > dtbeg_str) & (df['Date_of_report'] <= dtnow_str)]
    return dfwindow

def get_covid_dfdif_days(df,days,enddate=None):
    if enddate is None:
        now = datetime.now()
    else:
        now = datetime.strptime(enddate, '%Y-%m-%d')
    dtnow_str = now.strftime("%Y-%m-%d") + " 10:00:00"
    beg_date = now - timedelta(days=days)
    dtbeg_str = beg_date.strftime("%Y-%m-%d") + " 10:00:00"
    
    dfmin = df[(df['Date_of_report'] == dtbeg_str)][['Municipality_name','Total_reported','Hospital_admission','Deceased']]
    # This will assure NaN (ie. cases not attributed to a municipality) in this field get included in the groupby sum.
    dfmin['Municipality_name'] = dfmin['Municipality_name'].astype(str)
    dfmin= dfmin.groupby('Municipality_name', as_index=False).sum()
    dfmin.set_index('Municipality_name',inplace=True)
    
    dfmax = df[(df['Date_of_report'] == dtnow_str)][['Municipality_name','Total_reported','Hospital_admission','Deceased']]
    # This will assure NaN (ie. cases not attributed to a municipality) in this field get included in the groupby sum.
    dfmax['Municipality_name'] = dfmax['Municipality_name'].astype(str)
    dfmax= dfmax.groupby('Municipality_name', as_index=False).sum()
    dfmax.set_index('Municipality_name',inplace=True)
    return dfmax.sub(dfmin)
    

def get_file_end_datetime():
    with open(covidcnts_file, "rb") as file:
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR) 
        lastline = file.readline().decode()
        date,*strs = lastline.split(';')
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        
    
def cleanup():
    os.remove(covidcnts_file)

@click.command()
@click.option('--window', '-w', default=7,
              help="number of days to window the summary numbers by")
@click.option('--municipality', '-m', default='Amsterdam',
              help="Show Netherlands municipality specific numbers too")
@click.pass_context
def cli(ctx, window, municipality):
    download_covid_nums()

    df = pandas.read_csv(covidcnts_file, sep=';')

    df1 = get_covid_df_days(df,window)
    dfdif = get_covid_dfdif_days(df,1)

    print(df1.loc[df1['Municipality_name'] == municipality])

    filedate = get_file_end_datetime()
    today = datetime.today()
    lastdate = filedate.date().strftime('%Y-%m-%d')
    print(today,lastdate,today > filedate)
    if today.day > filedate.day:
        print(f'filedate {lastdate} doesn\'t match now {today.date()}')
        today = datetime.strptime(lastdate,'%Y-%m-%d')
    else:
        print(f'Todays publushed data {lastdate}')

    dfdif = get_covid_dfdif_days(df,window,enddate=lastdate)

    print(dfdif.sum())
    print(dfdif.loc[ municipality , : ])

    today_str = today.strftime("%Y-%m-%d")

    begin_str = '2020-05-01'
    begindate = datetime.strptime(begin_str, '%Y-%m-%d')
    nextday = begindate


    dates = []
    sums = []
    dfsum = pandas.DataFrame([],columns=['Total_reported','Hospital_admission','Deceased'])
    dfmunicipality = dfsum



    while begindate < today:
        next_str = begindate.strftime('%Y-%m-%d')
        dates.append(next_str)
        dfdif = get_covid_dfdif_days(df,window,enddate=next_str)
        newsum = dfdif.sum().to_frame().transpose()
        dfsum = dfsum.append(newsum, ignore_index=True)
        newam = dfdif.loc[ municipality , : ].to_frame().transpose()
        dfmunicipality = dfmunicipality.append(newam, ignore_index=True)
        begindate += timedelta(days=1)
        
    dfsum['Date'] = dates
    dfmunicipality['Date'] = dates

    # show only hospitalizations and mortality for all of The Netherlands
    ax = dfsum.plot(kind="line", x="Date", y="Hospital_admission", color='blue',figsize=(15,5),title=f'Netherlands {window}day window')
    #dfsum.plot(kind="line", x="Date", y="Total_reported",  ax=ax, color="black")
    dfsum.plot(kind="line",x="Date",y="Deceased",ax=ax,color="red")

    # show all for only Municipality
    ax = dfmunicipality.plot(kind="line", x="Date", y="Hospital_admission", color='blue',figsize=(15,5), title=f'{municipality} {window}day window')
    dfmunicipality.plot(kind="line", x="Date", y="Total_reported",  ax=ax, color="black")
    dfmunicipality.plot(kind="line",x="Date",y="Deceased",ax=ax,color="red")

    # show only hospitalizations and mortality for only Municipality
    ax = dfmunicipality.plot(kind="line", x="Date", y="Hospital_admission", color='blue',figsize=(15,5), title=f'{municipality} {window}day window')
    #dfmunicipality.plot(kind="line", x="Date", y="Total_reported",  ax=ax, color="black")
    dfmunicipality.plot(kind="line",x="Date",y="Deceased",ax=ax,color="red")

    plt.show()


if __name__ == "__main__":
    cli()
    cleanup()

