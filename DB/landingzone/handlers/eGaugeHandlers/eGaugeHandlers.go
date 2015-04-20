/*
 * Package contains functions to handle eGauge connections and network communication.
 */
package eGaugeHandlers

import (
	"log"
	"net/http"
	//"net/http/httputil"
	"bytes"

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
			packet, err := eGaugeDecoders.DecodePacket(buf.Bytes())
			if err != nil {
				log.Println("Error:", err)
				http.Error(res, err.Error(), http.StatusInternalServerError)
				return
			}
			log.Printf("Data:\n%#v\n", packet)

			err = db.InsertEGaugePacket(packet)
			if err != nil {
				log.Println("Error:", err)
				http.Error(res, err.Error(), http.StatusInternalServerError)
				return
			}
		}
	}
}
