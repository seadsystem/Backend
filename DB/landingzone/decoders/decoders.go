package decoders

import (
	"errors"
	"time"
)

type DataPoint struct {
	Serial int64
	Type   byte
	Device *string
	Data   int64
	Time   time.Time
}

type Iterator func() (*DataPoint, error)

func NewErrorIterator(err error) func() (*DataPoint, error) {
	return func() (*DataPoint, error) {
		return nil, err
	}
}

func NewEmptyIterator() func() (*DataPoint, error) {
	return NewErrorIterator(nil)
}

var NoData error = errors.New("no data in packet")
