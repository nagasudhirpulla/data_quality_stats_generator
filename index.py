# %%
import pandas as pd
import datetime as dt
import logging
from dataFetcher import fetchPntHistData
import numpy as np
from appUtils import addMonths
import argparse
logger = logging.getLogger(__name__)
# %%
# python index.py --file input/voltage_cs.xlsx --avg --max --min --sum --random
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input file path",
                    default="input/pnts.xlsx")
parser.add_argument(
    '--avg', help="Average row to be included", action='store_true')
parser.add_argument(
    '--sum', help="Sum row to be included", action='store_true')
parser.add_argument('--min', help="Min row to be included",
                    action='store_true')
parser.add_argument('--max', help="Max row to be included",
                    action='store_true')
parser.add_argument('--random', help="Use random data instead of real data",
                    action='store_true')
args = parser.parse_args()
fPath = args.file
isDumpAvg = args.avg
isDumpSum = args.sum
isDumpMax = args.max
isDumpMin = args.min
isRandom = args.random

pntsDf = pd.read_excel(fPath)
pntTags = pntsDf.iloc[:, 2].drop_duplicates()
# %%
# set start and end times for this month
nowDt = dt.datetime.now()
startDt = dt.datetime(nowDt.year, nowDt.month, 1)
endDt = addMonths(startDt, 1)-dt.timedelta(days=1)

# uncomment this if absolute times required
# startDtStr = dt.datetime(2020, 5, 1)
# endDtStr = dt.datetime(2020, 5, 31)

dateBinDays = 1
dateBinIntrvl = dt.timedelta(days=dateBinDays)
dateBins = pd.date_range(start=startDt, end=endDt, freq=dateBinIntrvl)
# %%
pntsQualityPercSumm = pd.DataFrame()
for pntItr in range(len(pntsDf)):
    pntId = pntsDf[pntsDf.columns[0]][pntItr].strip()
    pntName = pntsDf[pntsDf.columns[1]][pntItr].strip()
    pntGrp = pntsDf[pntsDf.columns[2]][pntItr].strip()
    print("itr = {0}, id = {1}, name = {2}, grp = {3}".format(
        pntItr+1, pntId, pntName, pntGrp))
    pntQualSumm = pd.DataFrame()
    for currDt in dateBins:
        # print("date = {0}".format(currDt))
        pntSampls = fetchPntHistData(
            pntId, currDt, currDt+dateBinIntrvl-dt.timedelta(seconds=1), logger=logger, isRandom=isRandom)
        pntQuals = [v['status'] for v in pntSampls]
        numSampls = len(pntQuals)
        if numSampls == 0:
            goodSamplsPerc = 0
        else:
            goodSamplsPerc = len([k for k in pntQuals if k in [
                'GOOD_LIMVIOL', 'GOOD']])*100/numSampls
        # goodSamplsPerc = round(goodSamplsPerc, 2)
        binQualSumm = pd.DataFrame(columns=['date', 'good_perc'], data=[
                                   [currDt, goodSamplsPerc]])
        pntQualSumm = pntQualSumm.append(binQualSumm, ignore_index=True)
    pntQualSumm['station'] = pntGrp
    # print(pntQualSumm)
    pntsQualityPercSumm = pntsQualityPercSumm.append(
        pntQualSumm, ignore_index=True)

# print(pntsQualityPercSumm)
# %%
pntsQualitySummary = pntsQualityPercSumm.pivot_table(
    index="date", columns="station", values="good_perc", aggfunc=np.max, fill_value=0)
summaryTags = [x for x in pntTags if x in pntsQualitySummary.columns]
pntsQualitySummary = pntsQualitySummary[summaryTags]
pntsQualitySummary.columns.name = None

reportDf = pntsQualitySummary

if isDumpAvg:
    # calculate average row
    avgRow = pd.DataFrame(pntsQualitySummary.mean(axis=0)).T
    reportDf = reportDf.append(avgRow)
    newIndex = reportDf.index.tolist()
    newIndex[-1] = "AVG"
    reportDf.index = newIndex

if isDumpSum:
    # calculate sum row
    sumRow = pd.DataFrame(pntsQualitySummary.sum(axis=0)).T
    reportDf = reportDf.append(sumRow)
    newIndex = reportDf.index.tolist()
    newIndex[-1] = "SUM"
    reportDf.index = newIndex

if isDumpMax:
    # calculate max row
    maxRow = pd.DataFrame(pntsQualitySummary.max(axis=0)).T
    reportDf = reportDf.append(maxRow)
    newIndex = reportDf.index.tolist()
    newIndex[-1] = "MAX"
    reportDf.index = newIndex

if isDumpMin:
    # calculate min row
    minRow = pd.DataFrame(pntsQualitySummary.min(axis=0)).T
    reportDf = reportDf.append(minRow)
    newIndex = reportDf.index.tolist()
    newIndex[-1] = "MIN"
    reportDf.index = newIndex

print(reportDf)

# %%
# nowTimeStr = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d-%H-%M-%S-%f")
monthTimeStr = dt.datetime.strftime(startDt, "%m-%Y")
dumpFilename = 'output/measQualSumm_{}.xlsx'.format(monthTimeStr)

with pd.ExcelWriter(dumpFilename) as writer:
    reportDf.to_excel(writer, index=True, sheet_name='data_avail')

# %%
print("Processing complete...")
