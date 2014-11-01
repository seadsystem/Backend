package handlers

import (
	"log"
	"net"
	"io"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

// Handle a client's request
func HandleRequest(conn net.Conn) {
	log.Println("Got a connection.")
	
	var buffer []byte
	tempbuf := make([]byte, constants.INPUT_BUFFER_SIZE)

	for {
		log.Println("Reading bytes...")
		n, err := conn.Read(tempbuf)
		if err != nil {
			if err != io.EOF {
				log.Println("read error:", err)
			}
			break
		}
		buffer = append(buffer, tempbuf[:n]...)

	}

	if len(buffer) < 1 {
		log.Println("Error: received empty request")
	} else {
		log.Println(buffer)
	}

	conn.Write([]byte("Response"))
	conn.Close()
}
