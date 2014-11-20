package database

import (
	"database/sql"
	"fmt"
	"log"

	"github.com/lib/pq"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

type DB struct {
	conn *sql.DB
}

func New() (DB, error) {
	conn, err := sql.Open("postgres", fmt.Sprintf("host=%s user=%s dbname=%s password=%s port=%d sslmode=disable", constants.DB_SOCKET, constants.DB_USER, constants.DB_NAME, constants.DB_PASSWORD, constants.DB_PORT))
	return DB{conn}, err
}

func (db DB) InsertRawPacket(data decoders.SeadPacket) {
	log.Println("Beginning transaction...")
	// Begin transaction
	txn, err := db.conn.Begin()
	if err != nil {
		log.Fatal(err)
	}

	// Prepare statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "data", "time"))
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Processing data...")

	// Process data
	data_type := string(data.Type)
	interp_time := data.Timestamp
	for _, element := range data.Data {
		log.Println("Data:", element)
		log.Println("Time:", interp_time)
		_, err = stmt.Exec(data.Serial, data_type, element, interp_time)
		interp_time = interp_time.Add(data.Period)
		if err != nil {
			log.Println(err)
			break
		}
	}

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
