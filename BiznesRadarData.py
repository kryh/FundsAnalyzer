import urllib3
import re
import os
import tempfile
import shutil
import asyncio
import aiohttp
import aiofiles

#url = "http://www.biznesradar.pl/notowania-historyczne/" + FUND_NAME + "," + PAGE_NR

folder = "GoBiznesRadar/"

@asyncio.coroutine
def getWebPage(fund, pageNumber):
	print("Downloading {}, page {}".format(fund, pageNumber))
	url = "http://www.biznesradar.pl/notowania-historyczne/" + fund + "," + str(pageNumber)
	
	response = yield from aiohttp.request('GET', url)
	html = yield from response.read()
	html = str(html)
	
	position_start = html.find("<table")
	position_end = html.find("</table")
	table = html[position_start:position_end]
	return table

#multiline string date value
def getValues(tabela): 
	START_TAG = "<td>"
	start_tagi = [m.start()+len(START_TAG) for m in re.finditer(START_TAG, tabela)]
	
	END_TAG = "</td>"
	end_tagi = [m.start() for m in re.finditer(END_TAG, tabela)]
	
	assert len(start_tagi) == len(end_tagi), "Cos nie tak z parsowaniem tablicy, tagi START i STOP sie nie zgadzaja"
	
	values = ""
	for i in range(0, len(start_tagi), 2):
		values += tabela[start_tagi[i]:end_tagi[i]] + " " + tabela[start_tagi[i+1]:end_tagi[i+1]] + "\n"

	return values

@asyncio.coroutine
def downloadFundData(fund):
	if not os.path.exists(folder+fund):

		myFile = yield from aiofiles.open(folder+fund, "w")
		try:
			coros = [getWebPage(fund, page) for page in range(1, 16)]
			tabela = yield from asyncio.gather(*coros)

			for PAGE_NR in range(1,16):  
				yield from myFile.write(getValues(tabela[PAGE_NR-1]))
				  
				print ("Finished:", fund, PAGE_NR)
		finally:
			yield from myFile.close()


	else:	# file exists, whole download unnecessary, only update
		# read first line to know how much needs to be downloaded
		with open(folder+fund, "r") as myFile:

			newestValueInFile = myFile.readline()
			
			values = ""

			for page in range(1,16):
				webPage = yield from getWebPage(fund, page)
				values += getValues(webPage)
				
				index = values.find(newestValueInFile)

				if index == 0:
					print("{} is up to date".format(fund))
					break
				elif index == -1:
					print("{} newest value from file not found on downloaded page, another needs to be downloaded".format(fund))
					continue
				else:
					print("{} needs to be updated".format(fund))
					newContent = values[:index]
					myFile.seek(0)
					oldContentList = myFile.readlines()

					oldContentString = ""
					for line in oldContentList:
						oldContentString += line

					myFile.close()
					os.remove(folder+fund)

					with open(folder+fund, "w") as myFile:
						myFile.write(newContent + oldContentString)

					break


@asyncio.coroutine
def whenReady(listOfFunds):
	coros = [downloadFundData(fund) for fund in listOfFunds]
	results = yield from asyncio.gather(*coros)


def Download(listOfFunds):		
	loop = asyncio.get_event_loop()
	loop.run_until_complete(whenReady(listOfFunds))
	loop.close()
