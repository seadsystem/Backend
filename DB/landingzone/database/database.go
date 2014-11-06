package database

import (
	"log"
	"fmt"
	"database/sql"

	"github.com/olt/pq"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

type DB struct {
	conn *sql.DB
}

func New() (db DB, err error) {
	db.conn, err := sql.Open("postgres", fmt.Sprintf("host=%s user=%s dbname=%s password=%s port=%d", constants.DB_SOCKET, constants.DB_USER, constants.DB_NAME, constants.DB_PASSWORD, constants.DB_PORT))
	return
}

func (db DB) InsertRaw(database_channel <-chan decoders.SeadPacket) {
	stmt, err := db.conn.Prepare("COPY data_raw (serial, type, data, time) FROM STDIN")
	// TODO: Add error handling

	for {
		log.Println("Waiting for data...")
		data := <-database_channel
		log.Println("Inserting data...")
		log.Printf("Data: %+v\n", data)
		_, err = stmt.Exec(data.Serial, data.Type, data.Data, data.Timestamp)
		// TODO: Add error handling
	}
}
