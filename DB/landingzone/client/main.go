package main

import (
	"flag"
//	"fmt"
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

func stringToChannelVector(channels string) []int {
	channels_vector := make([]int, 8, 8)
	for i := 0; i < len(channels); i++ {
		index := int(channels[i] - '0')
		channels_vector[index] = 1
	}
	return channels_vector
}


func main() {
//	num := flag.Int("n", 1, "Number of transmitters.")
	//serial := flag.Int64("serial", 0, "Serial number for client.")
	serial := int64(888888)
	timeout := flag.Duration("timeout", time.Second*30, "Timeout for a transmit.")
	//channels := flag.String("channels", "", "Channels to sample.")
	channels := "123457"

	flag.Parse()

	//isFatalError := false
	/*

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

	if *channels == "" {
		fmt.Fprintln(os.Stderr, "Error: Channels must be specified")
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
	*/
	host := "db.sead.systems:50051"

	// Set up a connection to the server.
	conn, err := grpc.Dial(host, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("could not connect: %v", err)
	}

	defer conn.Close()
	client := pb.NewLandingZoneClient(conn)

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

	channels_vector := stringToChannelVector(channels);

	var wg sync.WaitGroup

	packets := make([]chan *pb.Packet, 8)

	for i := 0; i < 8; i++ {
		packets[i] = make(chan *pb.Packet, bufferSize);
	}

	wg.Add(1)
	go func(){
		transmit.Transmit(ctx, client, packets, *timeout, channels_vector)
		wg.Done()
	}()

	gather.GatherData(ctx, packets, serial, channels_vector)

	wg.Wait()
	log.Println("Shutting down...")
}
