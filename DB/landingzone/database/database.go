/*
 * Package database handles connecting and writing to the database.
 */
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

		// Rollback transaction on error
		if err != nil {
			txn.Rollback()
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

/*
func (db DB) InsertSeadPacket(data seadPlugDecoders.SeadPacket) {
	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		log.Println(err)
		return
	}

	// Packet wide decelerations
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
		if constants.Verbose {
			log.Println("Data:", element)
			log.Println("Time:", interp_time)
		}

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

func (db DB) InsertEGaugePacket(packet eGaugeDecoders.Packet) (err error) {
	log.Println("Preliminary data processing...")

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

	// Select best data set
	if len(packet.Data) == 0 {
		log.Println("Error: No data in packet")
		return NoData
	}

	data := &packet.Data[0]
	columns := &data.Cnames
	for i := 1; i < len(packet.Data); i++ {
		if packet.Data[i].TimeDelta < data.TimeDelta {
			data = &packet.Data[i]
		}
	}

	// First and last rows don't contain data
	if len(data.Rows) < 1 {
		log.Println("Error: Packet only contains summary.")
		return NoData
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

	log.Println("Beginning transaction...")
	// Begin transaction. Required for bulk insert
	txn, err := db.conn.Begin()
	if err != nil {
		log.Println(err)
		return
	}

	log.Println("Columns:", *columns)
	interp_time := startTime // Set timestamp for first data point to time in packet
	var currData = make([]int64, len(*columns))

	// Prepare bulk insert statement
	stmt, err := txn.Prepare(pq.CopyIn("data_raw", "serial", "type", "device", "data", "time"))
	if err != nil {
		log.Println(err)
		goto closetrans
	}

	for _, row := range data.Rows {
		if constants.Verbose {
			log.Println("Row:", row.Columns)
			log.Println("Time:", interp_time)
		}

		if len(row.Columns) != len(*columns) {
			log.Println("Error: Invalid row.")
			continue
		}

		for i := 0; i < len(*columns); i++ {
			if data.DataDelta {
				currData[i] += row.Columns[i]
			} else {
				currData[i] = row.Columns[i]
			}
			if constants.Verbose {
				log.Printf(
					"%d, %s, %s, %d, %d, %v\n",
					serial,
					(*columns)[i].Type,
					(*columns)[i].Name,
					row.Columns[i],
					currData[i],
					interp_time,
				)
			}
			_, err = stmt.Exec(
				serial,
				(*columns)[i].Type,
				(*columns)[i].Name,
				currData[i],
				interp_time,
			) // Insert data. This is buffered.
			if err != nil {
				log.Println(err)
				break
			}
		}
		interp_time = interp_time.Add(time.Duration(data.TimeDelta) * time.Second * -1) // Add data point time spacing for next data point
	}

closetrans:
	log.Println("Closing off transaction...")

	// Flush buffer
	_, ferr := stmt.Exec()
	if ferr != nil {
		log.Fatal(ferr)
	}

	// Close prepared statement
	ferr = stmt.Close()
	if ferr != nil {
		log.Fatal(ferr)
	}

	// Commit transaction
	ferr = txn.Commit()
	if ferr != nil {
		log.Fatal(ferr)
	}

	log.Println("Transaction closed")

	return err
}
*/
