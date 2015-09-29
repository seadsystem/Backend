package database

import (
	"testing"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
)

func TestNewMock(t *testing.T) {
	db, err := NewMock()
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
