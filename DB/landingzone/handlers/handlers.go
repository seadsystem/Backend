package handlers

import (
	"errors"
	"io"
	"log"
	"net"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

// Errors
var Timeout = errors.New("Action timed out.")
var InvalidLength = errors.New("Invalid length header.")

// Handle a client's request
func HandleRequest(conn net.Conn) {
	log.Println("Got a connection.")

	serial, err := sync(conn)
	if err != nil {
		readError(err)
		return
	}

	for {
		log.Println("Reading length header...")
		length_header, err := readBytes(conn, constants.LENGTH_HEADER_SIZE)
		if err != nil {
			readError(err)
			break
		}

		data_length := int(length_header[1])

		// Check that we got a length header
		if length_header[0] != 'L' || data_length == 0 {
			log.Println("Invalid length header.")
			log.Println("Re-syncing...")
			conn.Write([]byte(constants.HEAD))
		} else {
			log.Printf("Length: %d\n", length_header[1])

			// Get the rest of the packet
			data, err := readBytes(conn, data_length-constants.LENGTH_HEADER_SIZE)

			if err != nil {
				readError(err)

				log.Println("Re-syncing...")
				conn.Write([]byte(constants.HEAD))
				break
			}

			log.Println("Read data:")
			log.Println(string(data))

			log.Println("Sending ACK.")
			conn.Write([]byte(constants.ACK))

			log.Println("Sending OKAY.")
			conn.Write([]byte(constants.OKAY))
		}

	}

	conn.Write([]byte("Response"))
	conn.Close()
}

func sync(conn net.Conn) (serial int, err error) {
	log.Println("Sending HEAD...")
	err = writePacket(conn, constants.HEAD)
	if err != nil {
		return
	}

	log.Println("Reading header...")
	data, err := readPacket(conn)
	if err != nil {
		return
	}

	// TODO Parse header to get serial
	serial = 0

	log.Println("Sending configuration...")

	log.Println("Sending OKAY.")
	err = writePacket(conn, constants.OKAY)
	if err != nil {
		return
	}

	return
}

func writePacket(conn net.Conn, data []byte) (err error) {
	write_length, err := conn.Write(data)
	if err != nil {
		return
	}
	if write_length != len(constants.ACK) {
		err = io.ErrShortWrite
		return
	}

	return
}

func readPacket(conn net.Conn) (data []byte, err error) {
	log.Println("Reading length header...")
	length_header, err := readBytes(conn, constants.LENGTH_HEADER_SIZE)
	if err != nil {
		return
	}

	data_length := int(length_header[1])

	// Check that we got a length header
	if length_header[0] != 'L' || data_length == 0 {
		err = InvalidLength
		return
	}

	log.Printf("Length: %d\n", length_header[1])

	// Get the rest of the packet
	data, err := readBytes(conn, data_length-constants.LENGTH_HEADER_SIZE)

	if err != nil {
		return
	}

	log.Println("Read data:")
	log.Println(string(data))

	log.Println("Sending ACK.")
	err = writePacket(conn, []byte(constants.ACK))
	if err != nil {
		return
	}

	return
}

// readError checks the error and prints an appropriate friendly error message.
func readError(err error) {
	if err != io.EOF {
		log.Println("Read error:", err)
	} else {
		log.Println("Done reading bytes.")
	}
}

// readBytes reads the specified number of bytes from the connection with an appropriate time limit.
func readBytes(conn net.Conn, bytes int) (data []byte, err error) {
	// Setup channels
	data_channel := make(chan []byte, 1)
	error_channel := make(chan error, 1)

	// Initiate read in new go routine
	go func() {
		buffer := make([]byte, bytes)
		n, ierr := conn.Read(buffer)
		if ierr != nil {
			error_channel <- ierr
			return
		}
		if bytes != n {
			error_channel <- io.ErrShortWrite
			return
		}
		data_channel <- buffer
	}()

	// Receive result of read
	select {
	case data = <-data_channel:
		// Read resulted in data
	case err = <-error_channel:
		// Read resulted in an error
	case <-time.After(time.Second * constants.READ_TIME_LIMIT):
		// Read timed out
		err = Timeout
	}

	return
}
