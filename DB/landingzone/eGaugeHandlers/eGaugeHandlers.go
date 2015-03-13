/*
 * Package contains functions to handle eGauge connections and network communication.
 */
package eGaugeHandlers

import (
	"log"
	"net/http"

	"github.com/seadsystem/Backend/DB/landingzone/database"
)

func HandleRequest(res http.ResponseWriter, req *http.Request, db database.DB) {
	log.Println("Got request from:", req.RemoteAddr)
	if req.Method == "POST" {
		log.Printf("Request from (%s) is of type POST\n", req.RemoteAddr)
		log.Printf("%+v\n", req.PostForm)
	}
}
