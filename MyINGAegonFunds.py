# import pprint
import matplotlib.pyplot as plt
# import os
import numpy as np
# import pandas as pd
import datetime

import BiznesRadarData

from optparse import OptionParser

# import aiofiles
# import asyncio

from prettytable import PrettyTable


def normalizeTable(table):
    # x = [t/table[0] for t in table]
    localTab = []
    for entrie in table:
        localTab.append([entrie[0], entrie[1] / table[0][1]])
    return localTab


def getTotalReturn(table):
    return table[-1] / table[0] - 1


def getDailyReturn(table):
    dailyRet = np.zeros(len(table))
    for i in range(1, len(table)):
        dailyRet[i] = table[i] / table[i - 1] - 1
    return dailyRet


def readLastNValuesFromBiznesRadarFileDates(filename, numberOfLastDays):
    with open(filename, 'r') as f:
        lines = f.readlines()
        lines.reverse()

        entries = []

        for line in lines:
            year = int(line.strip().split(" ")[0].split('.')[::-1][0])
            month = int(line.strip().split(" ")[0].split('.')[::-1][1])
            day = int(line.strip().split(" ")[0].split('.')[::-1][2])

            value = float(line.strip().split(' ')[1])

            entries.append([datetime.datetime(year, month, day), value])

        entries = entries[-numberOfLastDays:]
        entries = normalizeTable(entries)

        return entries


def DownsideDeviation(values):
    return np.sqrt(float(sum([min(0, x) ** 2 for x in values])) / len(values))

def calculateCovariance(fundA, fundB):
    cov = 0
    for i in range(len(fundA["dailyReturn"])):
        cov += (fundA["dailyReturn"][i] - fundA["meanDailyReturn"]) * (fundB["dailyReturn"][i] - fundB["meanDailyReturn"])

    cov = cov / len(fundA["dailyReturn"])
    return cov


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-D", "--Download", action='store_true', dest="Download", default=False,
                      help="Download ING stock data")
    (options, args) = parser.parse_args()

    INGFunds = [
        "UNIPIE.TFI", "INVPLO.TFI", "PZUGOT.TFI", "AVIDEP.TFI", "INGGOT.TFI", "INGDEL.TFI", "AVIOBD.TFI", "INGGDK.TFI",
        "PZUPDP.TFI", "AVIDPK.TFI",
        "UNIOBL.TFI", "INGOBL.TFI", "UNIONE.TFI", "INVOBA.TFI", "INVZEM.TFI", "PZUSWM.TFI", "UNISTW.TFI", "INGSWZ.TFI",
        "AVISTI.TFI", "INVZRO.TFI",
        "PZUZRO.TFI", "INGZRO.TFI", "UNIZRO.TFI", "AVIZRO.TFI", "INVZRW.TFI", "INVIII.TFI", "INGESD.TFI", "INVAKC.TFI",
        "PZUEME.TFI", "INVMSP.TFI",
        "INGGLM.TFI", "AVIAKA.TFI", "INGSEL.TFI", "INGGSD.TFI", "INGRWS.TFI", "INGSDY.TFI", "UNIAKC.TFI", "INGAKC.TFI",
        "AMPPIA.TFI", "AMPZAP.TFI",
        "AMPAAP.TFI", "INVIIC.TFI", "INGJAP.TFI", "WIG20", "WIG30", "mWIG40"
    ]

    folder = "GoBiznesRadar/"

    if options.Download:
        BiznesRadarData.Download(INGFunds)

    FundIndicators = []
    ScatterIndicators = []

    numberOfDays = 300

    # ==== ING Part ====

    # plt.subplot(1,2,1)

    AllFundData = {}

    for f in INGFunds:
        AllFundData[f] = {}

        AllFundData[f]["values"] = np.array(readLastNValuesFromBiznesRadarFileDates(folder + f, numberOfDays))
        AllFundData[f]["totalReturn"] = getTotalReturn(AllFundData[f]["values"][:, 1])
        AllFundData[f]["dailyReturn"] = getDailyReturn(AllFundData[f]["values"][:, 1])
        AllFundData[f]["stdDevDailyReturn"] = AllFundData[f]["dailyReturn"].std()
        AllFundData[f]["meanDailyReturn"] = AllFundData[f]["dailyReturn"].mean()
        AllFundData[f]["sharpeRatio"] = np.sqrt(len(AllFundData[f]["values"])) * AllFundData[f]["meanDailyReturn"] / AllFundData[f]["stdDevDailyReturn"]
        AllFundData[f]["sortinoRatio"] = np.sqrt(len(AllFundData[f]["values"])) * AllFundData[f]["meanDailyReturn"] / DownsideDeviation(AllFundData[f]["dailyReturn"])

        if (AllFundData[f]["sortinoRatio"] > 3.0 and AllFundData[f]["totalReturn"] > 0.03) or (f == "WIG20") or (f == "WIG30") or (f == "mWIG40"):
            FundIndicators.append(
                (f,
                 AllFundData[f]["totalReturn"],
                 AllFundData[f]["stdDevDailyReturn"],
                 AllFundData[f]["meanDailyReturn"],
                 AllFundData[f]["sharpeRatio"],
                 AllFundData[f]["sortinoRatio"],
                 AllFundData[f]["values"][:, 0],
                 AllFundData[f]["values"][:, 1]
                 ))

    print("\n")

    covarianceMatrix = np.zeros((len(INGFunds), len(INGFunds)))
    correlationMatrix = np.zeros((len(INGFunds), len(INGFunds)))

    for x, fx in enumerate(INGFunds):
        for y, fy in enumerate(INGFunds):
            covXY = calculateCovariance(AllFundData[fx], AllFundData[fy])
            covarianceMatrix[x][y] = covXY
            correlationMatrix[x][y] = covXY / (AllFundData[fx]["stdDevDailyReturn"] * AllFundData[fy]["stdDevDailyReturn"])

    # print(covarianceMatrix)

    print(correlationMatrix)

    # bestCorrelation = 0
    # for x, fx in enumerate(INGFunds):
    #     for y, fy in enumerate(INGFunds):
    #         if correlationMatrix[x][y] < bestCorrelation:
    #             bestCorrelation = correlationMatrix[x][y]
    #             print(fx, fy, bestCorrelation)


    pt = PrettyTable(["Name", "Total ret [%]", "Std dev daily ret", "Mean daily ret [%]", "Sharpe", "Sortino"])
    pt.align = 'r'
    pt.float_format = ".6"
    pt.float_format["Total ret [%]"] = ".2"
    pt.float_format["Sharpe"] = ".3"
    pt.float_format["Sortino"] = ".3"

    FundIndicators = sorted(FundIndicators, key=lambda x: (x[5], x[4]))
    FundIndicators.reverse()
    for f in FundIndicators[0:8]:
        trend3 = "+" if f[7][-4] < f[7][-3] else "-"
        trend2 = "+" if f[7][-3] < f[7][-2] else "-"
        trend1 = "+" if f[7][-2] < f[7][-1] else "-"

        pt.add_row([f[0], f[1]*100, f[2], f[3]*100, f[4], f[5]])

        # print("{0:<10}\ttotalRet {1:.5}, stdDevDailyRet {2:.5}, meanDailyRet {3:.5}, sharpeRatio {4:.5}, sortinoRatio {5:.5}".format(
        #         f[0], f[1], f[2], f[3], f[4], f[5]))
        plt.plot(f[6], (f[7] - 1) * 100,
                 label="{fundName},  Return: {totalRet:.2%}, sortino: {sortino:.4}, {trend3}{trend2}{trend1}".format(
                     fundName=f[0], totalRet=f[1], sortino=f[5], trend3=trend3, trend2=trend2, trend1=trend1))

    print(pt)

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('ING')
    plt.xlabel('dni')
    plt.ylabel('zysk %')

    figureManager = plt.get_current_fig_manager()
    figureManager.window.showMaximized()

    plt.show()
