/*
 * Package eGaugeHandlers contains functions to handle eGauge connections and network communication.
 */
package eGaugeHandlers

import (
	"bytes"
	"log"
	"net/http"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/eGaugeDecoders"
)

func HandleRequest(res http.ResponseWriter, req *http.Request, db database.DB) {
	log.Println("Got request from:", req.RemoteAddr)
	if req.Method != "POST" {
		http.Error(res, "Request method "+req.Method+" currently unsupported.", http.StatusInternalServerError)
		return
	}

	log.Printf("Request from (%s) is of type POST\n", req.RemoteAddr)
	if req.Body == nil {
		http.Error(res, "Request body must not be nil.", http.StatusInternalServerError)
		return
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(req.Body)

	if constants.Verbose {
		log.Println("Data:")
		log.Println(string(buf.Bytes()))
	}

	packet, err := eGaugeDecoders.DecodePacket(buf.Bytes())
	if err != nil {
		log.Println("Error decoding packet:", err)
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}

	if constants.Verbose {
		log.Printf("Data:\n%#v\n", packet)
	}

	iter, err := eGaugeDecoders.NewIterator(packet)
	if err != nil {
		log.Println("Error creating iterator from packet:", err)
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}

	if err := db.Insert(iter); err != nil {
		log.Println("Error:", err)
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}
}
