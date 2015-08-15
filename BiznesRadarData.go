package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"runtime"
	"strings"
	"sync"
)

var sem = make(chan struct{}, 15)

type container struct {
	fundname string
	data     string
}

type webPage struct {
	content string
}

func downloadWebPage(fund string, pageNum int) string {
	response, err := http.Get(fmt.Sprintf("http://www.biznesradar.pl/notowania-historyczne/%s,%d", fund, pageNum))
	if err != nil {
		panic(err)
	}
	defer response.Body.Close()

	contents, err := ioutil.ReadAll(response.Body)
	if err != nil {
		panic(err)
	}
	return string(contents)
}

func (wp webPage) getContent() string {
	return wp.content
}

func getTable(content string) string {
	start_index := strings.Index(content, "<table")
	stop_index := strings.Index(content, "</table")

	if start_index >= stop_index {
		panic(fmt.Sprintf("Wrong indexes of table: start_index=%d, stop_index=%d", start_index, stop_index))
	}

	table := content[start_index : stop_index+8]

	table = strings.Replace(table, "\n", "", -1)
	table = strings.Replace(table, " ", "", -1)
	table = strings.Replace(table, "\t", "", -1)
	return table
}

func isWIG(fundname string) bool {
    return strings.Contains(fundname, "WIG")
}

func DownloadFundData(fund string, pageNum int) string {

	page := downloadWebPage(fund, pageNum)
	table := getTable(page)
	data := ""

	//date value
	for {
		if isWIG(fund) { //Data Otwarcie Max Min Zamknięcie Obrót
			//parse date
			start_index := strings.Index(table, "<td>")

			if start_index == -1 {
				break
			}

			stop_index := strings.Index(table, "</td>")
			date := table[start_index+len("<td>") : stop_index]

			table = string(table)[stop_index+1:] //+1 in order to jump to next tag
			//parse value

			start_index = strings.Index(table, "<td>")
			stop_index = strings.Index(table, "</td>")
			/*otwarcie*/ _ = table[start_index+len("<td>") : stop_index]
			table = string(table)[stop_index+1:] //+1 in order to jump to next tag

            start_index = strings.Index(table, "<td>")
            stop_index = strings.Index(table, "</td>")
            /*max*/ _ = table[start_index+len("<td>") : stop_index]
            table = string(table)[stop_index+1:] //+1 in order to jump to next tag

            start_index = strings.Index(table, "<td>")
            stop_index = strings.Index(table, "</td>")
            /*min*/ _ = table[start_index+len("<td>") : stop_index]
            table = string(table)[stop_index+1:] //+1 in order to jump to next tag

            start_index = strings.Index(table, "<td>")
            stop_index = strings.Index(table, "</td>")
            zamkniecie := table[start_index+len("<td>") : stop_index]
            table = string(table)[stop_index+1:] //+1 in order to jump to next tag

            start_index = strings.Index(table, "<td>")
            stop_index = strings.Index(table, "</td>")
            /*obrot*/ _ = table[start_index+len("<td>") : stop_index]
            table = string(table)[stop_index+1:] //+1 in order to jump to next tag

			// fmt.Println(fund, date, value)
			data += fmt.Sprintf("%s %s\n", date, zamkniecie)

		} else {

			//parse date
			start_index := strings.Index(table, "<td>")

			if start_index == -1 {
				break
			}

			stop_index := strings.Index(table, "</td>")
			date := table[start_index+len("<td>") : stop_index]

			table = string(table)[stop_index+1:] //+1 in order to jump to next tag
			//parse value

			start_index = strings.Index(table, "<td>")
			stop_index = strings.Index(table, "</td>")
			value := table[start_index+len("<td>") : stop_index]
			table = string(table)[stop_index+1:] //+1 in order to jump to next tag

			// fmt.Println(fund, date, value)
			data += fmt.Sprintf("%s %s\n", date, value)
		}
	}

	return data
}

func main() {

	runtime.GOMAXPROCS(runtime.NumCPU())

	foldername := "GoBiznesRadar/"

	funds := []string{"UNIPIE.TFI", "INVPLO.TFI", "PZUGOT.TFI", "AVIDEP.TFI", "INGGOT.TFI", "INGDEL.TFI", "AVIOBD.TFI", "INGGDK.TFI", "PZUPDP.TFI", "AVIDPK.TFI",
		"UNIOBL.TFI", "INGOBL.TFI", "UNIONE.TFI", "INVOBA.TFI", "INVZEM.TFI", "PZUSWM.TFI", "UNISTW.TFI", "INGSWZ.TFI", "AVISTI.TFI", "INVZRO.TFI",
		"PZUZRO.TFI", "INGZRO.TFI", "UNIZRO.TFI", "AVIZRO.TFI", "INVZRW.TFI", "INVIII.TFI", "INGESD.TFI", "INVAKC.TFI", "PZUEME.TFI", "INVMSP.TFI",
		"INGGLM.TFI", "AVIAKA.TFI", "INGSEL.TFI", "INGGSD.TFI", "INGRWS.TFI", "INGSDY.TFI", "UNIAKC.TFI", "INGAKC.TFI", "AMPPIA.TFI", "AMPZAP.TFI",
		"AMPAAP.TFI", "INVIIC.TFI", "INGJAP.TFI", "WIG20", "WIG30", "mWIG40"}

	var wg sync.WaitGroup
	wg.Add(len(funds))

	for _, fund := range funds {

		go func(fund string) {
			sem <- struct{}{}

			if _, err := os.Stat(foldername + fund); err != nil {
				//file does not exist
				f, err := os.Create(foldername + fund)
				if err != nil {
					log.Fatal("Error during creating file: ", err)
				}
				defer f.Close()

				fundData := ""
				for i := 1; i <= 10; i++ {
					fundData += DownloadFundData(fund, i)
				}

				f.WriteString(fundData)

			} else {
				f, err := os.Open(foldername + fund)
				if err != nil {
					log.Fatal(err)
				} else {
					defer f.Close()

					scanner := bufio.NewScanner(f)
					scanner.Scan()
					firstLineFromFile := scanner.Text()

					fundData := ""
					i := 0
					for {
						i++

						fundData += DownloadFundData(fund, i)

						if index := strings.Index(fundData, firstLineFromFile); index == -1 {
							log.Printf("%s downloading page %d\n", fund, i)
							//need to download next page
							continue

						} else {
							//found index in that page
							if index == 0 {
								log.Printf("%s is up to date\n", fund) //nothing to do
								break
							} else {
								missingPart := fundData[:index]
								log.Printf("%s writing missing part: %s", fund, missingPart)

								oldContent, err := ioutil.ReadFile(foldername + fund)
								if err != nil {
									log.Print(err)
								} else {
									err := os.Remove(foldername + fund)
									if err != nil {
										log.Print(err)
									} else {
										f, err := os.Create(foldername + fund)
										if err != nil {
											log.Fatal("Error during creating file: ", err)
										}
										defer f.Close()
										f.WriteString(missingPart + string(oldContent))
										break
									}
								}
							}
						}
					}
				}
			}

			<-sem
			wg.Done()

		}(fund)
	}

	wg.Wait()

	fmt.Println("Done")
}
