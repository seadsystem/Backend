package main

import (
    "log"
    "net"

    "github.com/seadsystem/Backend/DB/landingzone/constants"
)

// Handle a client's request
func handleRequest (conn net.Conn) {
    buffer := make ([]byte, constants.INPUT_BUFFER_SIZE)
    requestLength, err := conn.Read (buffer)
    if err != nil {
        log.Println ("Error handling request: " + err.Error())
    } else if requestLength < 1 {
        log.Println ("Error: expected to receive request but got empty request")
    }

    conn.Write ([]byte("Response"))
    conn.Close()
}
