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
)

func HandleRequest(res http.ResponseWriter, req *http.Request, db database.DB) {
	log.Println("Got request from:", req.RemoteAddr)
	if req.Method == "POST" {
		log.Printf("Request from (%s) is of type POST\n", req.RemoteAddr)
	}

	/*data, err := httputil.DumpRequest(req, true)
	if err != nil {
		log.Println("Error dumping request:", err)
	} else {
		log.Println(string(data))
		log.Println("b2a:", req.PostFormValue("b2a"))
	}
	*/
	if req.Body != nil {
		buf := new(bytes.Buffer)
		buf.ReadFrom(req.Body)
		log.Println(string(buf.Bytes()))
	}
}
