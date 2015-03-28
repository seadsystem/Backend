/*
 * Package contains functions to handle eGauge connections and network communication.
 */
package eGaugeHandlers

import (
	"log"
	"net/http"
	"net/http/httputil"

	"github.com/seadsystem/Backend/DB/landingzone/database"
)

func HandleRequest(res http.ResponseWriter, req *http.Request, db database.DB) {
	log.Println("Got request from:", req.RemoteAddr)
	if req.Method == "POST" {
		log.Printf("Request from (%s) is of type POST\n", req.RemoteAddr)
	}

	data, err := httputil.DumpRequest(req, true)
	if err != nil {
		log.Println("Error dumping request:", err)
	} else {
		log.Println(string(data))
		log.Println("b2a:", http.PostFormValue("b2a"))
	}
}
