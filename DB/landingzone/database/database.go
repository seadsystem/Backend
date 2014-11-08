package database

import (
	"database/sql"
	"fmt"
	"log"
	"time"

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

func (db DB) InsertRaw(database_channel <-chan decoders.SeadPacket) {
	// Infinite loop with no breaks.
	for {
		log.Println("Waiting for data...")
		data := <-database_channel // Wait for first piece of data before starting transaction
		log.Println("Got data.")

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

	Data_processing:
		for {
			// Process data
			scale := constants.Scale[data.Type]
			data_type := string(data.Type)
			interp_time := data.Timestamp
			period := time.Duration(data.Period * float64(time.Second))
			for _, element := range data.Data {
				_, err = stmt.Exec(data.Serial, data_type, float32(element)*float32(scale), interp_time.Format(time.RFC3339))
				interp_time.Add(period)
				if err != nil {
					log.Println(err)
					break
				}
			}

			log.Println("Waiting for more data...")

			// Receive result of read
			select {
			case data = <-database_channel:
				log.Println("Got data.")
			case <-time.After(time.Second * constants.DB_TIME_LIMIT):
				log.Println("Transaction timed out.")
				break Data_processing
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
	scale := constants.Scale[data.Type]
	data_type := string(data.Type)
	interp_time := data.Timestamp
	period := time.Duration(data.Period * float64(time.Second))
	for _, element := range data.Data {
		_, err = stmt.Exec(data.Serial, data_type, float32(element)*float32(scale), interp_time.Format(time.RFC3339))
		interp_time.Add(period)
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
