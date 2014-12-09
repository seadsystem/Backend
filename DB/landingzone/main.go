/*
 * Package sets up connection listener and database and delegates new connections as they come in.
 */
package main

import (
	"log"
	"net"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/handlers"
)

func main() {
	// Set up connection
	listener, err := net.Listen("tcp4", constants.HOST+":"+constants.PORT) // The plugs only support IPv4.
	if err != nil {
		log.Println("Failed to open listener on port " + constants.PORT)
		log.Panic("Error was: " + err.Error())
	}
	defer listener.Close()

	// Setup database
	db, err := database.New()
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Listening for connections...")

	// Wait for requests forever
	for {
		conn, err := listener.Accept() // Blocking
		if err != nil {
			log.Println("Failed to accept request: " + err.Error())
			continue
		}
		go handlers.HandleRequest(conn, db) // Handle request in a new go routine
	}
}
