import urllib2
import re
import os
import tempfile
import shutil

#url = "http://www.biznesradar.pl/notowania-historyczne/" + FUND_NAME + "," + PAGE_NR

folder = "BiznesRadar/"

def getWebPage(fund, pageNumber):
	url = "http://www.biznesradar.pl/notowania-historyczne/" + fund + "," + str(pageNumber)
	response = urllib2.urlopen(url)
	html = response.read()

	position_start = html.find("<table")
	position_end = html.find("</table")
	table = html[position_start:position_end]
	return table

def downloadFundData(fund):
	if not os.path.exists(folder+fund):
		with open(folder+fund, "w") as myFile:
			for PAGE_NR in xrange(1,16):  

				tabela = getWebPage(fund, PAGE_NR)
				
				START_TAG = "<td>"
				start_tagi = [m.start()+len(START_TAG) for m in re.finditer(START_TAG, tabela)]
				
				END_TAG = "</td>"
				end_tagi = [m.start() for m in re.finditer(END_TAG, tabela)]
				
				assert len(start_tagi) == len(end_tagi), "Cos nie tak z parsowaniem tablicy, tagi START i STOP sie nie zgadzaja"
				
				for i in xrange(0, len(start_tagi), 2):
					myFile.write(tabela[start_tagi[i]:end_tagi[i]] + " " + tabela[start_tagi[i+1]:end_tagi[i+1]] + "\n")
				  
				print "Finished:", fund, PAGE_NR

	else:	# file exists, whole download unnecessary, only update
		# read first line to know how much needs to be downloaded
		with open(folder+fund, "r") as myFile:			

			newestValueInFile = myFile.readline()
			lastDateFromFile, _ = newestValueInFile.split(" ")

			with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpFundFile:				

				for PAGE_NR in xrange(1,16):  

					tabela = getWebPage(fund, PAGE_NR)
					
					START_TAG = "<td>"
					start_tagi = [m.start()+len(START_TAG) for m in re.finditer(START_TAG, tabela)]
					
					END_TAG = "</td>"
					end_tagi = [m.start() for m in re.finditer(END_TAG, tabela)]
					
					assert len(start_tagi) == len(end_tagi), "Cos nie tak z parsowaniem tablicy, tagi START i STOP sie nie zgadzaja"
		
					for i in xrange(0, len(start_tagi), 2):
						dateFromNet = tabela[start_tagi[i]:end_tagi[i]]
						valueFromNet = tabela[start_tagi[i+1]:end_tagi[i+1]]
						print dateFromNet, lastDateFromFile

						if PAGE_NR == 1 and i == 0 and (dateFromNet == lastDateFromFile):
							#data is up to date, no download needed, cleanup
							tmpFundFile.close()
							myFile.close()
							os.unlink(tmpFundFile.name)
							print "Data for '{}' is up to date".format(fund)
							return

						if dateFromNet != lastDateFromFile:	#newer values downloaded

							tmpFundFile.write(dateFromNet + " " + valueFromNet + "\n")
						else: #got to the existing values in file
							#write old file content to tmp fole
							tmpFundFile.write(newestValueInFile)
							tmpFundFile.writelines(myFile.readlines())

							tmpFundFile.close()
							myFile.close()

							shutil.move(tmpFundFile.name, myFile.name)

							print "Finished updating:", fund, PAGE_NR
							return


			#open tmp file
			#write values from net to tmp file
			#write content of fund file to tmp file
			#remove fund file
			#rename tmp file to fund file

def Download(listOfFunds):
  
 for fund in listOfFunds:
 	downloadFundData(fund)
 		


























"""


import urllib2
import re

#url = "http://www.biznesradar.pl/notowania-historyczne/" + FUND_NAME + "," + PAGE_NR


def Download():
  
  funds = [
  "UNIPIE.TFI", "INVPLO.TFI", "PZUGOT.TFI", "AVIDEP.TFI", "INGGOT.TFI", "INGDEL.TFI", "AVIOBD.TFI", "INGGDK.TFI", "PZUPDP.TFI", "AVIDPK.TFI", 
  "UNIOBL.TFI", "INGOBL.TFI", "UNIONE.TFI", "INVOBA.TFI", "INVZEM.TFI", "PZUSWM.TFI", "UNISTW.TFI", "INGSWZ.TFI", "AVISTI.TFI", "INVZRO.TFI", 
  "PZUZRO.TFI", "INGZRO.TFI", "UNIZRO.TFI", "AVIZRO.TFI", "INVZRW.TFI", "INVIII.TFI", "INGESD.TFI", "INVAKC.TFI", "PZUEME.TFI", "INVMSP.TFI", 
  "INGGLM.TFI", "AVIAKA.TFI", "INGSEL.TFI", "INGGSD.TFI", "INGRWS.TFI", "INGSDY.TFI", "UNIAKC.TFI", "INGAKC.TFI"
  ]

  folder = "BiznesRadar/"
  
  for fund in funds:
    
    with open(folder+fund, "w") as myFile:
      for PAGE_NR in xrange(1,16):
	  
	url = "http://www.biznesradar.pl/notowania-historyczne/" + fund + "," + str(PAGE_NR)
	response = urllib2.urlopen(url)
	html = response.read()

	#print html #entire page content
	
	position_start = html.find("<table")
	position_end = html.find("</table")
      
	tabela = html[position_start:position_end]
	
	START_TAG = "<td>"
	start_tagi = [m.start()+len(START_TAG) for m in re.finditer(START_TAG, tabela)]
	
	END_TAG = "</td>"
	end_tagi = [m.start() for m in re.finditer(END_TAG, tabela)]
	
	assert len(start_tagi) == len(end_tagi), "Cos nie tak z parsowaniem tablicy, tagi START i STOP sie nie zgadzaja"
	
	for i in xrange(0, len(start_tagi), 2):
	  myFile.write(tabela[start_tagi[i]:end_tagi[i]] + " " + tabela[start_tagi[i+1]:end_tagi[i+1]] + "\n")
	  
	print "Finished:", fund, PAGE_NR
    
  
if __name__ == "__main__":
  Download()"""