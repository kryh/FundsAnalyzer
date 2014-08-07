import pprint
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import datetime

import BiznesRadarData

from optparse import OptionParser


def normalizeTable(table):
	#x = [t/table[0] for t in table]
	localTab = []
	for entrie in table:
		localTab.append([entrie[0], entrie[1]/table[0][1]])
	return localTab


def totalReturn(table):
	return table[-1]/table[0]-1


def dailyReturn(table):
	dailyRet = np.zeros(len(table))
	for i in range(1, len(table)):
		dailyRet[i] = table[i]/table[i-1]-1
	return dailyRet


def readValuesFromFile(filename):
	f = open(filename, 'r')
	firstline = f.readline()
	del firstline
	lines = f.readlines()
	f.close()
	
	lines = [float(line.strip().split(',')[5]) for line in lines][-numberOfDays:]
	lines = normalizeTable(lines)
	return lines

def readLastNValuesFromBiznesRadarFile(filename, numberOfLastDays):
	with open(filename, 'r') as f:
		lines = f.readlines()
		lines.reverse()
		values = [float(line.strip().split(' ')[1]) for line in lines][-numberOfLastDays:]
		values = normalizeTable(values)
		return values


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

			entries.append( [datetime.datetime(year, month, day), value] )
		
		entries = entries[-numberOfLastDays:]
		entries = normalizeTable(entries)

		return entries



def DownsideDeviation(values):
	return np.sqrt(float(sum([min(0,x)**2 for x in values]))/len(values))



if __name__ == "__main__":

	parser = OptionParser()
	parser.add_option("-D", "--Download", action='store_true', dest="Download", default=False, help="Download ING stock data")
	(options, args) = parser.parse_args()

	INGFunds = [
		"UNIPIE.TFI", "INVPLO.TFI", "PZUGOT.TFI", "AVIDEP.TFI", "INGGOT.TFI", "INGDEL.TFI", "AVIOBD.TFI", "INGGDK.TFI", "PZUPDP.TFI", "AVIDPK.TFI", 
		"UNIOBL.TFI", "INGOBL.TFI", "UNIONE.TFI", "INVOBA.TFI", "INVZEM.TFI", "PZUSWM.TFI", "UNISTW.TFI", "INGSWZ.TFI", "AVISTI.TFI", "INVZRO.TFI", 
		"PZUZRO.TFI", "INGZRO.TFI", "UNIZRO.TFI", "AVIZRO.TFI", "INVZRW.TFI", "INVIII.TFI", "INGESD.TFI", "INVAKC.TFI", "PZUEME.TFI", "INVMSP.TFI", 
		"INGGLM.TFI", "AVIAKA.TFI", "INGSEL.TFI", "INGGSD.TFI", "INGRWS.TFI", "INGSDY.TFI", "UNIAKC.TFI", "INGAKC.TFI"
		]

	AegonFunds = [
		"ALLSEL.TFI", "ALLPIE.TFI", "BPHOB1.TFI", "AVIOBL.TFI", "AVIAKP.TFI", "AVISTI.TFI", "AVIZRO.TFI", "INVBRI.TFI", "INVAKC.TFI", "INVMSP.TFI", "INVZRO.TFI", 
		"INGZRO.TFI", "LEGAKC.TFI", "LEGSSP.TFI", "LEGSTR.TFI", "NOBAKC.TFI", "NOBAMS.TFI", "NOBMIE.TFI", "PKOPLU.TFI", "PKOPDP.TFI", "PKOSKA.TFI", "PZUAMS.TFI", 
		"PZUZRO.TFI", "SKAAKC.TFI", "SKAMSS.TFI", "SKATFS.TFI", "UNIAKC.TFI", "UNIPIE.TFI", "UNIZRO.TFI", "UNISTW.TFI", "AVINTE.TFI", "AVINSP.TFI", "QUEAGR.TFI", 
		"QUESEL.TFI", "QUEOKA.TFI", "NOBTIM.TFI", "PZUBIN.TFI", "INVGOO.TFI", "INVIIC.TFI", "INVAML.TFI", "NOBGLR.TFI", "NOBSWP.TFI", "INGGSD.TFI", "PZUEME.TFI",
		"NOBAFR.TFI", "ARKOBL.TFI", "PKODLG.TFI", "UNITTD.TFI", "AVIDPK.TFI"
 		]

	folder = "BiznesRadar/"

	if options.Download:
		BiznesRadarData.Download(INGFunds + AegonFunds)


	FundIndicators = []

	numberOfDays = 300

# ==== ING Part ====

	plt.subplot(2,1,1)

	for f in INGFunds:
		#values = readLastNValuesFromBiznesRadarFile(folder+f, numberOfDays)
		values = np.array(readLastNValuesFromBiznesRadarFileDates(folder+f, numberOfDays))
		totalRet = totalReturn(values[:,1])
		dailyRet = dailyReturn(values[:,1])
		stdDevDailyRet = dailyRet.std()
		meanDailyRet = dailyRet.mean()
		sharpeRatio = np.sqrt(len(values))*meanDailyRet/stdDevDailyRet
		sortinoRatio = np.sqrt(len(values))*meanDailyRet/DownsideDeviation(dailyRet)

		if sortinoRatio > 3 and totalRet > 0.03:
			FundIndicators.append((f, totalRet, stdDevDailyRet, meanDailyRet, sharpeRatio, sortinoRatio, values[:,0], values[:,1]))


	print "\n"

	
	FundIndicators = sorted(FundIndicators, key=lambda x: (x[5], x[4])) 
	FundIndicators.reverse()
	for f in FundIndicators[0:8]:
		print "{0:<10}\ttotalRet {1:.5}, stdDevDailyRet {2:.5}, meanDailyRet {3:.5}, sharpeRatio {4:.5}, sortinoRatio {5:.5}".format(f[0], f[1], f[2], f[3], f[4], f[5])
		plt.plot(f[6], f[7], label="{fundName},  Return: {totalRet:.2%}, sortino: {sortino:.4}".format(fundName=f[0], totalRet=f[1], sortino=f[5]))

	plt.legend(loc='best')
	plt.grid(True)
	plt.title('ING')
	plt.xlabel('dni')


# ==== ING Part ====


# ==== Aegon Part ====

	FundIndicators = []

	plt.subplot(2,1,2)

	for f in AegonFunds:
		values = np.array(readLastNValuesFromBiznesRadarFileDates(folder+f, numberOfDays))
		totalRet = totalReturn(values[:,1])
		dailyRet = dailyReturn(values[:,1])
		stdDevDailyRet = dailyRet.std()
		meanDailyRet = dailyRet.mean()
		sharpeRatio = np.sqrt(len(values))*meanDailyRet/stdDevDailyRet
		sortinoRatio = np.sqrt(len(values))*meanDailyRet/DownsideDeviation(dailyRet)

		if sortinoRatio > 3 and totalRet > 0.03:
			FundIndicators.append((f, totalRet, stdDevDailyRet, meanDailyRet, sharpeRatio, sortinoRatio, values[:,0], values[:,1]))


	print "\n"

	
	FundIndicators = sorted(FundIndicators, key=lambda x: (x[5], x[4])) 
	FundIndicators.reverse()
	for f in FundIndicators[0:8]:
		print "{0:<10}\ttotalRet {1:.5}, stdDevDailyRet {2:.5}, meanDailyRet {3:.5}, sharpeRatio {4:.5}, sortinoRatio {5:.5}".format(f[0], f[1], f[2], f[3], f[4], f[5])
		plt.plot(f[6], f[7], label="{fundName},  Return: {totalRet:.2%}, sortino: {sortino:.4}".format(fundName=f[0], totalRet=f[1], sortino=f[5]))

# ==== Aegon Part ====



	plt.legend(loc='best')
	plt.grid(True)
	plt.title('Aegon')
	plt.xlabel('dni')
	plt.ylabel('zysk %')


	figureManager = plt.get_current_fig_manager()
	figureManager.window.showMaximized()

	plt.show()
