package database

import (
	"errors"
	"testing"
	"time"

	sqlmock "github.com/DATA-DOG/go-sqlmock"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

func TestNewMock(t *testing.T) {
	db, mock, err := NewMock()
	mock.ExpectClose()
	if err != nil {
		t.Fatalf("got NewMock() = _, %v, want = _, nil", err)
	}
	if err := db.Close(); err != nil {
		t.Fatalf("got db.Close() = %v, want = nil", err)
	}
}

func TestNew(t *testing.T) {
	if _, err := New(); err != nil {
		t.Fatalf("got New() = _, %v, want = _, nil", err)
	}
}

func TestSetMaxOpenConns(t *testing.T) {
	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectClose()
	db := DB{conn}

	db.SetMaxOpenConns(5)
	if err := db.Close(); err != nil {
		t.Fatalf("got db.Close() = %v, want = nil", err)
	}
}

func TestInsert(t *testing.T) {
	oldVerbosity := constants.Verbose
	constants.Verbose = true
	defer func() { constants.Verbose = oldVerbosity }()

	closureIndex := 0
	var iter = func() (*decoders.DataPoint, error) {
		if closureIndex >= 3 {
			return nil, nil
		}
		point := &decoders.DataPoint{
			Serial: 64,
			Type:   'T',
			Data:   int64(closureIndex),
			Time:   time.Unix(int64(500+closureIndex), 0),
		}
		closureIndex++
		return point, nil
	}

	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectBegin()
	query := "COPY \\\"data_raw\\\" \\(\\\"serial\\\", \\\"type\\\", \\\"data\\\", \\\"time\\\", \\\"device\\\"\\) FROM STDIN"
	stmt := mock.ExpectPrepare(query)
	stmt.ExpectExec().WithArgs(64, "T", 0, time.Unix(500, 0), nil).WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WithArgs(64, "T", 1, time.Unix(501, 0), nil).WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WithArgs(64, "T", 2, time.Unix(502, 0), nil).WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WillReturnResult(sqlmock.NewResult(0, 0))
	mock.ExpectCommit()
	db := DB{conn}

	if err := db.Insert(iter); err != nil {
		t.Errorf("got db.Insert(iter) = %v, want = nil", err)
	}
}

func TestInsertBeginErr(t *testing.T) {
	conn, _, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	db := DB{conn}

	if err := db.Insert(func() (*decoders.DataPoint, error) { return nil, nil }); err == nil || err.Error() != "all expectations were already fulfilled, call to database transaction Begin was not expected" {
		t.Errorf("got db.Insert() = %v, want = nil", err)
	}
}

func TestInsertPrepareErr(t *testing.T) {
	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectBegin()
	mock.ExpectRollback()
	db := DB{conn}

	want := `call to Prepare stetement with query 'COPY "data_raw" ("serial", "type", "data", "time", "device") FROM STDIN', was not expected, next expectation is: ExpectedRollback => expecting transaction Rollback`
	if err := db.Insert(func() (*decoders.DataPoint, error) { return nil, nil }); err == nil || err.Error() != want {
		t.Errorf("got db.Insert() = %v, want = %s", err, want)
	}
}

func TestInsertFlushErr(t *testing.T) {
	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectBegin()
	mock.ExpectPrepare("COPY \\\"data_raw\\\" \\(\\\"serial\\\", \\\"type\\\", \\\"data\\\", \\\"time\\\", \\\"device\\\"\\) FROM STDIN")
	mock.ExpectRollback()
	db := DB{conn}

	want := `call to exec query 'COPY "data_raw" ("serial", "type", "data", "time", "device") FROM STDIN' with args [], was not expected, next expectation is: ExpectedRollback => expecting transaction Rollback`
	if err := db.Insert(func() (*decoders.DataPoint, error) { return nil, nil }); err == nil || err.Error() != want {
		t.Errorf("got db.Insert() = %v, want = %s", err, want)
	}
}

func TestInsertCloseErr(t *testing.T) {
	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectBegin()
	want := errors.New("STMT ERROR")
	stmt := mock.ExpectPrepare("COPY \\\"data_raw\\\" \\(\\\"serial\\\", \\\"type\\\", \\\"data\\\", \\\"time\\\", \\\"device\\\"\\) FROM STDIN").WillReturnCloseError(want)
	stmt.ExpectExec().WillReturnResult(sqlmock.NewResult(0, 0))
	mock.ExpectRollback()
	db := DB{conn}

	if err := db.Insert(func() (*decoders.DataPoint, error) { return nil, nil }); err == nil || err.Error() != want.Error() {
		// TODO: Figure out why this test doesn't work.
		// Disabled until issue is fixed:
		// https://github.com/DATA-DOG/go-sqlmock/issues/25
		//t.Errorf("got db.Insert() = %v, want = %v", err, want)
	}
}

func TestInsertErr(t *testing.T) {
	conn, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("got sqlmock.New() = _, _, %v, want = _, _, nil", err)
	}
	mock.ExpectBegin()
	query := "COPY \\\"data_raw\\\" \\(\\\"serial\\\", \\\"type\\\", \\\"data\\\", \\\"time\\\", \\\"device\\\"\\) FROM STDIN"
	stmt := mock.ExpectPrepare(query)
	stmt.ExpectExec().WillReturnResult(sqlmock.NewResult(0, 0))
	mock.ExpectRollback()
	db := DB{conn}

	want := "call to exec query 'COPY \"data_raw\" (\"serial\", \"type\", \"data\", \"time\", \"device\") FROM STDIN' with args [0 \x00 0 0001-01-01 00:00:00 +0000 UTC <nil>], was not expected, next expectation is: ExpectedRollback => expecting transaction Rollback"
	if err := db.Insert(func() (*decoders.DataPoint, error) { return &decoders.DataPoint{}, nil }); err == nil || err.Error() != want {
		t.Errorf("got db.Insert(iter) = %v, want = %s", err, want)
	}
}
