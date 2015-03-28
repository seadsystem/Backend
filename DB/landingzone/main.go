/*
 * Package sets up connection listener and database and delegates new connections as they come in.
 */
package main

import (
	"log"
	"net"
	"net/http"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/handlers/eGaugeHandlers"
	"github.com/seadsystem/Backend/DB/landingzone/handlers/seadPlugHandlers"
)

func main() {

	// Setup database
	db, err := database.New()
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Listening for connections...")

	go httpListener(eGaugeHandlers.HandleRequest, constants.EGAUGE_PORT, db)
	go listener(seadPlugHandlers.HandleRequest, constants.RPI_1_PORT, db)
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

func httpListener(handler func(http.ResponseWriter, *http.Request, database.DB), port string, db database.DB) {
	serverMux := http.NewServeMux()

	// Setup HTTP handler for all URLs on the specified port.
	serverMux.HandleFunc("/", func(res http.ResponseWriter, req *http.Request) { handler(res, req, db) })

	http.ListenAndServe(constants.HOST+":"+port, serverMux)
}
