package handlers

import (
	"errors"
	"io"
	"log"
	"net"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

// Errors
var Timeout = errors.New("Action timed out.")
var InvalidLength = errors.New("Invalid length header.")

// HandleRequest handles a communication stream with a plug.
func HandleRequest(conn net.Conn, database_channel chan<- decoders.SeadPacket) {
	log.Println("Got a connection.")

	var err error

	// Do initial sync to get serial number and start receiving data
	_, err = sync(conn)
	if err != nil {
		readError(err)
		return
	}

	// Main data receiving loop
	for {
		packet, err := readPacket(conn)

		if err != nil {
			readError(err)

			log.Println("Re-syncing...")
			_, err = sync(conn)
			if err != nil {
				readError(err)
				break
			}
			continue
		}

		log.Println("Read data:")
		log.Println(string(packet))

		log.Println("Parsing data...")
		data, err := decoders.DecodePacket(packet)
		if err != nil {
			readError(err)
			break
		}
		log.Printf("Data: %+v\n", data)

		// TODO: Write data to database

		log.Println("Sending ACK...")
		writePacket(conn, []byte(constants.ACK))
		if err != nil {
			readError(err)
			break
		}
	}

	log.Println("Closing connection...")
	conn.Close()
}

// sync re-aligns the packets, resets the plug's configuration and resumes data transfer.
func sync(conn net.Conn) (serial int, err error) {
	log.Println("Sending HEAD...")
	err = writePacket(conn, []byte(constants.HEAD))
	if err != nil {
		return
	}

	log.Println("Reading header...")
	data, err := readPacket(conn)
	if err != nil {
		return
	}

	log.Println("Parsing header for serial...")
	serial, err = decoders.DecodeHeader(data)
	if err != nil {
		return
	}
	log.Printf("Plug serial: %d\n", serial)

	//log.Println("Sending configuration...")
	// TODO: Send config

	log.Println("Sending OKAY...")
	err = writePacket(conn, []byte(constants.OKAY))
	if err != nil {
		return
	}

	return
}

// writePacket writes a message to the specified connection with proper error handling.
func writePacket(conn net.Conn, data []byte) (err error) {
	write_length, err := conn.Write(data)
	if err != nil {
		return
	}
	if write_length != len(data) {
		err = io.ErrShortWrite
		return
	}

	return
}

// readPacket reads in an entire packet (including length prefix) with proper error handling. The packet's payload (the entire packet minus the length prefix) is returned.
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
	data, err = readBytes(conn, data_length-constants.LENGTH_HEADER_SIZE)
	if err != nil {
		return
	}

	log.Println("Read data:")
	log.Println(string(data))

	log.Println("Sending ACK...")
	err = writePacket(conn, []byte(constants.ACK))
	if err != nil {
		return
	}

	return
}

// readError checks the error and prints an appropriate friendly error message.
func readError(err error) {
	if err == io.EOF {
		log.Println("Done reading bytes.")
	} else {
		log.Println("Read error: ", err)
	}
}

// readBytes reads the specified number of bytes from the connection with a time limit store in constants.READ_TIME_LIMIT. The timeout kills unneeded connections and helps unstick stuck plug interactions.
func readBytes(conn net.Conn, bytes int) (data []byte, err error) {
	// Setup channels
	data_channel := make(chan []byte, 1)
	error_channel := make(chan error, 1)

	// Initiate read in new go routine to enable timeouts
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
