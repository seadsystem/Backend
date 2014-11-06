package database

import (
	"log"

	//"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

func init() {
	// TODO: Initiate connection to the database
}

func InsertRaw(database_channel <-chan decoders.SeadPacket) {
	for {
		log.Println("Waiting for data...")
		data := <-database_channel
		log.Println("Inserting data:")
		log.Printf("Data: %+v\n", data)
	}
}
