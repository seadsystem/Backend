package eGaugeHandlers

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
)

func reqOnly(req *http.Request, err error) *http.Request {
	return req
}

func TestHandle(t *testing.T) {
	oldVerbosity := constants.Verbose
	constants.Verbose = true
	defer func() { constants.Verbose = oldVerbosity }()

	db, mock, err := database.NewMock()
	mock.ExpectClose()
	if err != nil {
		t.Fatalf("Creating mock DB: %v", err)
	}

	tests := []struct {
		req  *http.Request
		res  string
		name string
	}{
		{reqOnly(http.NewRequest("GET", "", nil)), "Request method GET currently unsupported.\n", "GET method"},
		{reqOnly(http.NewRequest("POST", "", nil)), "Request body must not be nil.\n", "nil body"},
		{reqOnly(http.NewRequest("POST", "", bytes.NewBufferString("foo"))), "EOF\n", "invalid XML"},
		{reqOnly(http.NewRequest("POST", "", bytes.NewBufferString(`<group serial="xxx"></group>`))), "reading serial: strconv.ParseInt: parsing \"xxx\": invalid syntax\n", "invalid serial"},
		{reqOnly(http.NewRequest("POST", "", bytes.NewBufferString(`<group serial="5"><data time_stamp="5"></data></group>`))), "call to database transaction Begin, was not expected, next expectation is: ExpectedClose => expecting database Close\n", "a valid request"},
	}
	for _, test := range tests {
		res := httptest.NewRecorder()
		HandleRequest(res, test.req, db)

		buf := new(bytes.Buffer)
		buf.ReadFrom(res.Body)
		if res.Code != http.StatusInternalServerError || string(buf.Bytes()) != test.res {
			t.Errorf("Handling request with %s. Got = %v, %q, want = %v, %q", test.name, res.Code, string(buf.Bytes()), http.StatusInternalServerError, test.res)
		}
	}

	if err := db.Close(); err != nil {
		t.Fatalf("got db.Close() = %v, want = nil", err)
	}
}
