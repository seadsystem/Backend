/*
 * Package database handles connecting and writing to the database.
 */
package database

import (
	"database/sql"
	"fmt"
	"log"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
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

func NewMock() (DB, error) {
	conn, mock, err := sqlmock.New()
	mock.ExpectClose()
	return DB{conn}, err
}

func (db DB) Close() error {
	return db.conn.Close()
}

func (db DB) SetMaxOpenConns(n int) {
	db.conn.SetMaxOpenConns(n)
}

func (db DB) Insert(iter decoders.Iterator) (err error) {
	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		return
	}

	// Prepare bulk insert statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "data", "time", "device"))

	// Cleanup either when done or in the case of an error
	defer func() {
		log.Println("Closing off transaction...")

		if stmt != nil {
			// Flush buffer
			if _, eerr := stmt.Exec(); eerr != nil {
				if err == nil {
					err = eerr
				}
			}

			// Close prepared statement
			if cerr := stmt.Close(); cerr != nil {
				if err == nil {
					err = cerr
				}
			}
		}

		// Rollback transaction on error
		if err != nil {
			txn.Rollback()
			log.Println("Transaction rolled back")
			return
		}

		// Commit transaction
		err = txn.Commit()

		log.Println("Transaction closed")
	}()

	// Check for error from preparing statement
	if err != nil {
		return
	}

	for {
		var row *decoders.DataPoint
		row, err = iter()
		if row == nil || err != nil {
			break
		}

		if constants.Verbose {
			log.Println("Data:", row.Data)
			log.Println("Time:", row.Time)
		}

		// Insert data. This is buffered.
		if _, err = stmt.Exec(row.Serial, row.Type, row.Data, row.Time, row.Device); err != nil {
			break
		}
	}
	return
}
