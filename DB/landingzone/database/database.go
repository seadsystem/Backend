package database

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/olt/pq"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

type DB struct {
	conn *sql.DB
}

func New() (db DB, err error) {
	conn, err := sql.Open("postgres", fmt.Sprintf("host=%s user=%s dbname=%s password=%s port=%d", constants.DB_SOCKET, constants.DB_USER, constants.DB_NAME, constants.DB_PASSWORD, constants.DB_PORT))
	db.set(conn)
	return
}

func (db DB) set(conn *sql.DB) {
	db.conn = conn
}

func (db DB) InsertRaw(database_channel <-chan decoders.SeadPacket) {
	stmt, err := db.conn.Prepare("COPY data_raw (serial, type, data, time) FROM STDIN")
	if err != nil {
		log.Fatal(err)
	}

	for {
		log.Println("Waiting for data...")
		data := <-database_channel
		log.Println("Inserting data...")
		log.Printf("Data: %+v\n", data)
		_, err = stmt.Exec(data.Serial, data.Type, data.Data, data.Timestamp)
		if err != nil {
			log.Println(err)
		}
	}
}
