/*
 * Package handles connecting and writing to the database.
 */
package database

import (
	"database/sql"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/lib/pq"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/eGaugeDecoders"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/seadPlugDecoders"
)

type DB struct {
	conn *sql.DB
}

func New() (DB, error) {
	conn, err := sql.Open("postgres", fmt.Sprintf("host=%s user=%s dbname=%s password=%s port=%d sslmode=disable", constants.DB_SOCKET, constants.DB_USER, constants.DB_NAME, constants.DB_PASSWORD, constants.DB_PORT))
	return DB{conn}, err
}

func (db DB) InsertSeadPacket(data seadPlugDecoders.SeadPacket) {
	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		log.Println(err)
		return
	}

	// Packet wide declerations
	data_type := string(data.Type)
	interp_time := data.Timestamp // Set timestamp for first data point to time in packet

	// Prepare bulk insert statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "data", "time"))
	if err != nil {
		log.Println(err)
		goto closetrans
	}

	log.Println("Processing data...")

	// Process data
	for _, element := range data.Data {
		log.Println("Data:", element)
		log.Println("Time:", interp_time)
		_, err = stmt.Exec(data.Serial, data_type, element, interp_time) // Insert data. This is buffered.
		interp_time = interp_time.Add(data.Period)                       // Add data point time spacing for next data point
		if err != nil {
			log.Println(err)
			break
		}
	}

closetrans:
	log.Println("Closing off transaction...")

	// Flush buffer
	_, err = stmt.Exec()
	if err != nil {
		log.Fatal(err)
	}

	// Close prepared statement
	err = stmt.Close()
	if err != nil {
		log.Fatal(err)
	}

	// Commit transaction
	err = txn.Commit()
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Transaction closed")
}

func (db DB) InsertEGaugePacket(packet eGaugeDecoders.Packet) {
	log.Println("Peliminary data processing...")

	// Process data packet
	log.Println("Reading serial:", packet.Serial)
	serial, err := strconv.ParseInt(packet.Serial, 0, 64)
	if err != nil || serial <= 0 {
		log.Println()
		if err != nil {
			log.Println("Error reading serial:", err)
		} else {
			log.Println("Invalid serial:", serial)
		}
		return
	}

	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		log.Println(err)
		return
	}

	// Select best data set
	if len(packet.Data) == 0 {
		log.Println("Error: No data in packet")
		return
	}

	data := &packet.Data[0]
	columns := &data.Cnames
	for i := 1; i < len(packet.Data); i++ {
		if packet.Data[i].Delta < data.Delta {
			data = &packet.Data[i]
		}
	}

	// Get data set start time
	log.Println("Reading start time:", data.Timestamp)
	startUnixTime, err := strconv.ParseInt(data.Timestamp, 0, 64)
	if err != nil || startUnixTime <= 0 {
		log.Println()
		if err != nil {
			log.Println("Error reading start time:", err)
		} else {
			log.Println("Invalid start time:", startUnixTime)
		}
		return
	}
	startTime := time.Unix(startUnixTime, 0)

	log.Println("Columns:", *columns)
	interp_time := startTime // Set timestamp for first data point to time in packet

	// Prepare bulk insert statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "device", "data", "time"))
	if err != nil {
		log.Println(err)
		goto closetrans
	}

	for _, row := range data.Rows {
		log.Println("Row:", row.Columns)
		log.Println("Time:", interp_time)
		if len(row.Columns) != len(*columns) {
			log.Println("Error: Invalid row.")
			continue
		}
		for i := 0; i < len(*columns); i++ {
			_, err = stmt.Exec(serial,
				(*columns)[i].Type,
				(*columns)[i].Name,
				row.Columns[i],
				interp_time,
			) // Insert data. This is buffered.
			if err != nil {
				log.Println(err)
				break
			}
		}
		interp_time = interp_time.Add(time.Duration(data.Delta) * time.Second) // Add data point time spacing for next data point
	}

closetrans:
	log.Println("Closing off transaction...")

	// Flush buffer
	_, err = stmt.Exec()
	if err != nil {
		log.Fatal(err)
	}

	// Close prepared statement
	err = stmt.Close()
	if err != nil {
		log.Fatal(err)
	}

	// Commit transaction
	err = txn.Commit()
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Transaction closed")
}
