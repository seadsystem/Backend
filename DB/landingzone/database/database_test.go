package database

import "testing"

func TestNewMock(t *testing.T) {
	db, err := NewMock()
	if err != nil {
		t.Fatalf("got NewMock() = _, %v, want = _, nil", err)
	}
	if err := db.Close(); err != nil {
		t.Fatalf("got db.Close() = %v, want = nil", err)
	}
}
