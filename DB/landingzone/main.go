/*
 * Package sets up connection listener and database and delegates new connections as they come in.
 */
package main

import (
	"flag"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"sync"

	"google.golang.org/grpc"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/handlers/eGaugeHandlers"
	"github.com/seadsystem/Backend/DB/landingzone/handlers/grpcHandlers"
	"github.com/seadsystem/Backend/DB/landingzone/handlers/seadPlugHandlers"
)

func main() {
	logLevel := flag.Int("log", 0, "Logging level. 0=No logging, 1=Most logging, 2=Log data.")
	flag.Parse()

	if *logLevel <= 0 {
		log.SetOutput(ioutil.Discard)
	}
	if *logLevel >= 2 {
		constants.Verbose = true
	}

	// Setup database
	db, err := database.New()
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Causes operations which require a new connection to block instead of failing.
	db.SetMaxOpenConns(constants.DB_MAX_CONNS)

	log.Println("Listening for connections...")

	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		wg.Done()
		log.Fatal(grpcListener(grpcHandlers.Register, constants.GRPC_PORT, db))
	}()
	go func() {
		wg.Done()
		log.Fatal(httpListener(eGaugeHandlers.HandleRequest, constants.EGAUGE_PORT, db))
	}()
	wg.Wait() // Wait for background servers to get a chance to start.
	listener(seadPlugHandlers.HandleRequest, constants.SEAD_PLUG_PORT, db)
}

func listener(handler func(net.Conn, database.DB), port string, db database.DB) {
	// Set up connection
	listener, err := net.Listen("tcp4", constants.HOST+":"+port) // The plugs only support IPv4.
	if err != nil {
		log.Println("Failed to open listener on port " + port)
		log.Panic("Error was: " + err.Error())
	}
	defer listener.Close()

	// Wait for requests forever
	for {
		conn, err := listener.Accept() // Blocking
		if err != nil {
			log.Println("Failed to accept request: " + err.Error())
			continue
		}
		go handler(conn, db) // Handle request in a new go routine. The database object is thread safe.
	}
}

func httpListener(handler func(http.ResponseWriter, *http.Request, database.DB), port string, db database.DB) error {
	serverMux := http.NewServeMux()

	// Setup HTTP handler for all URLs on the specified port.
	serverMux.HandleFunc("/", func(res http.ResponseWriter, req *http.Request) { handler(res, req, db) })

	return http.ListenAndServe(constants.HOST+":"+port, serverMux)
}

func grpcListener(register func(*grpc.Server, database.DB), port string, db database.DB) error {
	lis, err := net.Listen("tcp", constants.HOST+":"+port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	register(s, db)
	return s.Serve(lis)
}
