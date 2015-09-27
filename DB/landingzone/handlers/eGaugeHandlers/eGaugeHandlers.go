/*
 * Package contains functions to handle eGauge connections and network communication.
 */
package eGaugeHandlers

import (
	"log"
	"net/http"
	//"net/http/httputil"
	"bytes"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/eGaugeDecoders"
)

func HandleRequest(res http.ResponseWriter, req *http.Request, db database.DB) {
	log.Println("Got request from:", req.RemoteAddr)
	if req.Method == "POST" {
		log.Printf("Request from (%s) is of type POST\n", req.RemoteAddr)
		if req.Body != nil { // Should always be true according to spec
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
	}
}
