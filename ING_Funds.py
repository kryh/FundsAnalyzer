import pprint
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

import BiznesRadarData

from optparse import OptionParser


def normalizeTable(table):
	x = [t/table[0] for t in table]
	return x


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


def DownsideDeviation(values):
	return np.sqrt(float(sum([min(0,x)**2 for x in values]))/len(values))



if __name__ == "__main__":

	parser = OptionParser()
	parser.add_option("-D", "--Download", action='store_true', dest="Download", default=False, help="Download ING stock data")
	(options, args) = parser.parse_args()

	if options.Download:
		BiznesRadarData.Download()

	folder = 'BiznesRadar/'
	Funds = os.listdir(folder)

	FundIndicators = []

	numberOfDays = 300

	for f in Funds:
		values = readLastNValuesFromBiznesRadarFile(folder+f, numberOfDays)
		totalRet = totalReturn(values)
		dailyRet = dailyReturn(values)
		stdDevDailyRet = dailyRet.std()
		meanDailyRet = dailyRet.mean()
		sharpeRatio = np.sqrt(len(values))*meanDailyRet/stdDevDailyRet
		sortinoRatio = np.sqrt(len(values))*meanDailyRet/DownsideDeviation(dailyRet)

		if sortinoRatio > 4 and totalRet > 0.03:
			FundIndicators.append((f, totalRet, stdDevDailyRet, meanDailyRet, sharpeRatio, sortinoRatio, values))


	print "\n"

	
	plt.subplot(2,1,1)

	FundIndicators = sorted(FundIndicators, key=lambda x: (x[5], x[4])) 
	FundIndicators.reverse()
	for f in FundIndicators[0:8]:
		print "{0:<10}\ttotalRet {1:.5}, stdDevDailyRet {2:.5}, meanDailyRet {3:.5}, sharpeRatio {4:.5}, sortinoRatio {5:.5}".format(f[0], f[1], f[2], f[3], f[4], f[5])
		plt.plot(f[6], label="{fundName},  Return: {totalRet:.2%}, sortino: {sortino:.4}".format(fundName=f[0], totalRet=f[1], sortino=f[5]))



	plt.legend(loc='best')
	plt.grid(True)
	plt.title('ING')
	plt.xlabel('dni')
	plt.ylabel('zysk %')
	figureManager = plt.get_current_fig_manager()
	figureManager.window.showMaximized()
	plt.show()
