package decoders

import (
	"errors"
	"testing"
)

func TestNewIterator(t *testing.T) {
	testerr := errors.New("TEST ERR")
	tests := []struct {
		iter Iterator
		err  error
	}{
		{NewEmptyIterator(), nil},
		{NewErrorIterator(testerr), testerr},
	}

	for _, test := range tests {
		for i := 0; i < 5; i++ {
			if _, err := test.iter(); err != test.err {
				t.Errorf("got = %v, want = %v", err, test.err)
			}
		}
	}
}
