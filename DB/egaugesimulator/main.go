package main

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

func simulate(url string, serial int) {
	for {
		go func() {
			data := bytes.NewBufferString(sample)
			_, err := http.Post(url, "application/xml", data)
			if err != nil {
				log.Println("Error:", err)
			}
		}

		time.Sleep(2 * time.Second)
	}
}

func main() {
	num := flag.Int("n", 1, "Number of eGauges.")
	flag.Parse()

	// Check for remote URL
	if flag.NArg() != 1 {
		fmt.Println("Error: Remote URL must be specified.")
		fmt.Println("Default flag values:")
		flag.PrintDefaults()
		os.Exit(1)
	}
	url := flag.Arg(0)

	for i := 1; i <= *num; i++ {
		go simulate(url, i)
	}

	// Block forever as all processing is in other goroutines.
	select {}
}

const sample = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="0x1bcd005e">
<data columns="3" time_stamp="0x55036c9e" time_delta="1" delta="true" epoch="0x54914d54">
 <cname t="P">heater</cname>
 <cname t="P">lamp</cname>
 <cname t="P">lamp+</cname>
 <r><c>-379726</c><c>1346313</c><c>2748</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>188</c><c>188</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>62</c><c>0</c></r>
 <r><c>61</c><c>61</c><c>0</c></r>
 <r><c>62</c><c>61</c><c>0</c></r>
 <r><c>61</c><c>62</c><c>0</c></r>
 <r><c>204431</c><c>332</c><c>0</c></r>
</data>
<data time_stamp="0x55036c2c" time_delta="60">
 <r><c>-204431</c><c>-332</c><c>0</c></r>
 <r><c>568</c><c>29</c><c>0</c></r>
 <r><c>296</c><c>14</c><c>0</c></r>
 <r><c>296</c><c>14</c><c>0</c></r>
 <r><c>296</c><c>14</c><c>0</c></r>
 <r><c>296</c><c>14</c><c>0</c></r>
 <r><c>296</c><c>14</c><c>0</c></r>
</data>
</group>`
