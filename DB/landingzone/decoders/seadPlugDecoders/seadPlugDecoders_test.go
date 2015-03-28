package seadPlugDecoders

import (
	"testing"

	"github.com/seadsystem/Backend/DB/landingzone/decoders/seadPlugDecoders"
)

func TestDoubleToAsciiTime(t *testing.T) {
	input := 1393540108
	expected := "1612822282800000"
	result := decoders.DoubleToAsciiTime(float64(input))
	if result != expected {
		t.Errorf("Failed to convert double to ascii time, got %s instead of %s", result, expected)
	}
}

func TestAsciiTimeToDouble(t *testing.T) {
	input := "1612822282800000"
	expected := 14012548.28
	result, err := decoders.AsciiTimeToDouble([]byte(input))
	if result != expected || err != nil {
		t.Errorf("Failed to convert ascii time to double, got %d instead of %d", result, expected)
	}
}

func TestBinary2uint(t *testing.T) {
	//func Binary2uint(data []byte) (total uint)
	input := []byte{'\x5d', '\x01'}
	expected := uint(93 + 256)
	result := decoders.Binary2uint(input)
	if result != expected {
		t.Errorf("Failed to convert binary to uint, got %d instead of %d", result, expected)
	}
}
