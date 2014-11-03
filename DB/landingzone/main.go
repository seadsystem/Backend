package main

import (
	"log"
	"net"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	//"github.com/seadsystem/Backend/DB/landingzone/decoders"
	"github.com/seadsystem/Backend/DB/landingzone/handlers"
)

func main() {
	listener, err := net.Listen("tcp4", constants.HOST+":"+constants.PORT)
	if err != nil {
		log.Println("Failed to open listener on port " + constants.PORT)
		log.Panic("Error was: " + err.Error())
	}
	defer listener.Close()

	log.Println("Listening for connections...")

	// Handle requests in a go routine
	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Failed to accept request: " + err.Error())

		}
		handlers.HandleRequest(conn)
	}
}
