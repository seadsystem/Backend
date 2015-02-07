/*
 * Package handles connecting and writing to the database.
 */
package database

import (
	"database/sql"
	"fmt"
	"log"
	"net/url"

	"github.com/influxdb/influxdb/client"
	"github.com/lib/pq"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

type DB struct {
	conn    *sql.DB
	infconn *client.Client
}

func New() (DB, error) {
	postgres, err := NewPostgres()
	if err != nil {
		return DB{nil, nil}, err
	}

	influx, err := NewInflux()
	if err != nil {
		return DB{nil, nil}, err
	}

	return DB{postgres.conn, influx.infconn}, nil
}

func NewPostgres() (DB, error) {
	conn, err := sql.Open("postgres", fmt.Sprintf("host=%s user=%s dbname=%s password=%s port=%d sslmode=disable", constants.DB_SOCKET, constants.DB_USER, constants.DB_NAME, constants.DB_PASSWORD, constants.DB_PORT))

	return DB{conn, nil}, err
}

func NewInflux() (DB, error) {
	influxURL, err := url.Parse(
		fmt.Sprintf(
			"%s://%s:%d",
			constants.INFLUX_PROTOCOL,
			constants.INFLUX_HOST,
			constants.INFLUX_PORT,
		),
	)
	if err != nil {
		return DB{nil, nil}, err
	}

	infconn, err := client.NewClient(
		client.Config{
			*influxURL,
			constants.INFLUX_USERNAME,
			constants.INFLUX_PASSWORD,
		},
	)
	return DB{nil, infconn}, err
}

func (db DB) InsertRawPacket(data decoders.SeadPacket) {
	if db.conn != nil {
		db.postgresInsertRawSeadPacket(data)
	}
	if db.infconn != nil {
		db.influxInsertRawSeadPacket(data)
	}
}

func (db DB) postgresInsertRawSeadPacket(data decoders.SeadPacket) {
	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		log.Fatal(err)
	}

	// Prepare bulk insert statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "data", "time"))
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Processing data...")

	// Process data
	data_type := string(data.Type)
	interp_time := data.Timestamp // Set timestamp for first data point to time in packet
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

func (db DB) influxInsertRawSeadPacket(data decoders.SeadPacket) {
	log.Println("Processing data...")
	
	// Setup write
	dbWrite := client.Write{constants.INFLUX_DB_NAME, "", []client.Point{}}

	// Process data
	data_type := string(data.Type)
	interp_time := data.Timestamp // Set timestamp for first data point to time in packet
	for _, element := range data.Data {
		log.Println("Data:", element)
		log.Println("Time:", interp_time)
		
		// Insert data.
		dbWrite.Points = append(
			dbWrite.Points, // Slice of data points
			
			// New point
			client.Point{
				Name: fmt.Sprintf("%s.%d", constants.INFLUX_SEAD_PLUG_PREFIX, data.Serial),
				Timestamp: client.Timestamp(interp_time),
				Values: map[string]interface{}{data_type: element},
				Precision: "n",
			},
		)
		
		interp_time = interp_time.Add(data.Period)    // Add data point time spacing for next data point
	}
	
	log.Println("Writing data.")
	_, err := db.infconn.Write(dbWrite)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Data processed.")
}
