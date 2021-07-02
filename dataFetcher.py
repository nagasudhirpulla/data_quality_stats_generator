"""
@author: Nagasudhir Pulla
"""
import requests
import json
import datetime as dt
import random


def makeTwoDigits(num):
    if(num < 10):
        return "0"+str(num)
    return num


def fetchPntHistData(pnt, startTime, endTime, fetchStrategy='snap', secs=60, logger=None, isRandom=False):
    if isRandom:
        return fetchPntHistDataRandom(pnt, startTime, endTime, fetchStrategy, secs, logger)
    
    startTimeStr = startTime.strftime('%d/%m/%Y/%H:%M:%S')
    endTimeStr = endTime.strftime('%d/%m/%Y/%H:%M:%S')
    
    params = dict(
        pnt=pnt,
        strtime=startTimeStr,
        endtime=endTimeStr,
        secs=secs,
        type=fetchStrategy
    )
    data = []
    try:
        # http://localhost:62448/api/values/history?pnt=WP.SCADA.F12453472&strtime=12/12/2019/00:00:00&endtime=13/12/2019/00:00:00&secs=900&type=average
        r = requests.get(
            url="http://localhost:62448/api/values/history", params=params)
        data = json.loads(r.text)
        r.close()
    except Exception as e:
        data = []
        logger.error(e)
    return data


def fetchPntHistDataRandom(pnt, startTime, endTime, fetchStrategy='snap', secs=300, logger=None):
    data = []
    if startTime > endTime:
        return data
    samplPeriod = secs
    samplPeriod = 60 if samplPeriod == 0 else samplPeriod

    curTime = startTime
    while curTime <= endTime:
        data.append({"dval": random.randint(-50, 50),
                     "timestamp": dt.datetime.strftime(curTime, "%Y-%m-%dT%H:%M:%S"),
                     "status": "GOOD"})
        curTime += dt.timedelta(seconds=samplPeriod)
    return data
