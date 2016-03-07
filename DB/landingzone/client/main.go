package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"time"

	"golang.org/x/net/context"
	"google.golang.org/grpc"

	"github.com/seadsystem/Backend/DB/landingzone/client/gather"
	"github.com/seadsystem/Backend/DB/landingzone/client/transmit"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

const bufferSize = 10

func main() {
	num := flag.Int("n", 1, "Number of transmitters.")
	serial := flag.Int64("serial", 0, "Serial number for client.")
	timeout := flag.Duration("timeout", time.Second*30, "Timeout for a transmit.")
	flag.Parse()

	isFatalError := false

	// Check for remote host
	if flag.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "Error: Remote host must be specified")
		isFatalError = true
	}

	if *num <= 0 {
		fmt.Fprintln(os.Stderr, "Error: Number of transmitters must be positive")
		isFatalError = true
	}

	if *serial <= 0 {
		fmt.Fprintln(os.Stderr, "Error: Serial number must be positive")
		isFatalError = true
	}

	if *timeout <= 0 {
		fmt.Fprintln(os.Stderr, "Error: Transmit timeout must be positive")
		isFatalError = true
	}

	if isFatalError {
		fmt.Fprintf(os.Stderr, "Usage: %s [flags] host\n", os.Args[0])
		fmt.Fprintln(os.Stderr, "Example host: localhost:50051")
		fmt.Fprintln(os.Stderr, "Default flag values:")
		flag.PrintDefaults()
		os.Exit(1)
	}

	host := flag.Arg(0)

	// Set up a connection to the server.
	conn, err := grpc.Dial(host, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("could not connect: %v", err)
	}

	defer conn.Close()
	client := pb.NewLandingZoneClient(conn)

	c := make(chan *pb.Packet, bufferSize)
	ctx, cancel := context.WithCancel(context.Background())

	sigc := make(chan os.Signal, 1)
	signal.Notify(sigc, os.Interrupt)
	go func() {
		for range sigc {
			// sig is a ^C, handle it
			log.Println("Shutting down gracefully...")
			cancel()
		}
	}()

	var wg sync.WaitGroup

	for i := 1; i <= *num; i++ {
		wg.Add(1)
		go func() {
			transmit.Transmit(ctx, client, c, *timeout)
			wg.Done()
		}()
	}

	gather.GatherData(ctx, c, *serial)

	wg.Wait()
	log.Println("Shutting down...")
}
