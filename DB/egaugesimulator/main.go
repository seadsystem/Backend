package main

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"text/template"
	"time"
)

var reportTemplate *template.Template

func init() {
	reportTemplate = template.Must(template.New("reportTemplate").Parse(reportTemplateText))
}

// The maximum concurrent connections that the database is configured to handle.
const MaxDBConns = 95

func transmit(url string, serial int, epoch int64, timeout time.Duration) {
	client := http.Client{
		Timeout: timeout,
	}

	content := map[string]interface{}{}
	content["epoch"] = epoch
	content["serial"] = serial
	content["timestamp"] = time.Now().Unix()

	data := [rows][columns]int32{}
	for row := 0; row < rows; row++ {
		for column := 0; column < columns; column++ {
			data[row][column] = rand.Int31()
		}
	}
	content["data"] = data

	buf := bytes.Buffer{}
	reportTemplate.Execute(&buf, content)

	resp, err := client.Post(url, "application/xml", &buf)
	if err != nil {
		log.Println("Error:", err)
		if len(buf.Bytes()) > 0 {
			log.Println("Data:")
			log.Println(string(buf.Bytes()))
		}
		return
	}

	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		log.Printf("eGauge simulator #%d with serial 0x%08x successfully sent data.\n", serial, serial)
	} else {
		log.Printf("eGauge simulator #%d with serial 0x%08x received HTTP error code %s:\n", serial, serial, resp.Status)

		buf := new(bytes.Buffer)
		buf.ReadFrom(resp.Body)
		log.Println(string(buf.Bytes()))
	}
}

func simulate(url string, serial int, timeout time.Duration) {
	epoch := time.Now().Unix()

	log.Printf("Starting eGauge simulator #%d with serial 0x%08x at time 0x%08x.\n", serial, serial, epoch)

	for {
		// Data "gathering" time
		time.Sleep(time.Minute)

		go transmit(url, serial, epoch, timeout)
	}
}

func main() {
	num := flag.Int("n", 1, "Number of eGauges.")
	flag.Parse()

	isFatalError := false

	// Check for remote URL
	if flag.NArg() != 1 {
		fmt.Println("Error: Remote URL must be specified.")
		isFatalError = true
	}

	if *num <= 0 {
		fmt.Println("Error: Number of eGauges must be positive.")
		isFatalError = true
	}

	if isFatalError {
		fmt.Println("Default flag values:")
		flag.PrintDefaults()
		os.Exit(1)
	}

	url := flag.Arg(0)

	timeout := time.Minute / time.Duration(*num) * time.Duration(MaxDBConns)

	for i := 1; i <= *num; i++ {
		go simulate(url, i, timeout)

		// Spread out egauge reports
		time.Sleep(time.Minute / time.Duration(*num))
	}

	log.Println("Finished starting eGauge simulators.")

	// Block forever as all processing is in other goroutines.
	select {}
}

const (
	rows               = 62
	columns            = 3
	reportTemplateText = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="{{.serial | printf "0x%08x"}}">
<data columns="3" time_stamp="{{.timestamp | printf "0x%08x"}}" time_delta="1" delta="true" epoch="{{.epoch | printf "0x%08x"}}">
 <cname t="P">heater</cname>
 <cname t="P">lamp</cname>
 <cname t="P">lamp+</cname>{{range $row_number, $row := $.data}}
 <r>{{range $col_number, $point := $row}}<c>{{$point}}</c>{{end}}</r>{{end}}
</data>
</group>`
)
