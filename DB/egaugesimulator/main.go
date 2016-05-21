package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/seadsystem/Backend/DB/egaugesimulator/transmit"
)

// The maximum concurrent connections that the database is configured to handle.
const MaxDBConns = 95

func transmitAndLog(url string, serial int, epoch int64, timeout time.Duration) {
	if err := transmit.Transmit(url, serial, time.Now().Unix(), epoch, timeout); err != nil {
		log.Printf("eGauge simulator #%d with serial 0x%08x received %v", serial, serial, err)
	}
	log.Printf("eGauge simulator #%d with serial 0x%08x successfully sent data.\n", serial, serial)
}

func simulate(url string, serial int, timeout time.Duration) {
	epoch := time.Now().Add(-time.Minute).Unix()

	//log.Printf("Starting eGauge simulator #%d with serial 0x%08x at time 0x%08x.\n", serial, serial, epoch)

	for {
		go transmitAndLog(url, serial, epoch, timeout)

		// Data "gathering" time
		time.Sleep(time.Minute)
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

	//log.Println("Finished starting eGauge simulators.")

	// Block forever as all processing is in other goroutines.
	select {}
}
