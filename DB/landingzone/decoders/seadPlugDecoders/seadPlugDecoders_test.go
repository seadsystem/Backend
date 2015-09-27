package seadPlugDecoders

import (
	"errors"
	"fmt"
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

func errorEqual(err1, err2 error) bool {
	if err1 == nil || err2 == nil {
		return err1 == err2
	}
	return err1.Error() == err2.Error()
}

func TestAsciiTimeToDuration(t *testing.T) {
	tests := []struct {
		input string
		want  time.Duration
		err   error
	}{
		{
			"1612822282800000",
			14012548*time.Second + 280*time.Millisecond,
			nil,
		},
		{
			"16128222828000000",
			0,
			errors.New("invalid ascii time: 16128222828000000"),
		},
		{
			"-161282228280000",
			0,
			errors.New("invalid ascii time: -161282228280000"),
		},
	}
	for _, test := range tests {
		got, err := AsciiTimeToDuration([]byte(test.input))
		if got != test.want || !errorEqual(err, test.err) {
			t.Errorf("Failed to convert ascii time to duration: got AsciiTimeToDuration(%s) = %v, %v, want = %v, %v", test.input, got, err, test.want, test.err)
		}
	}
}

func TestBinary2uint(t *testing.T) {
	input := []byte{'\x5d', '\x01'}
	expected := uint(93 + 256)
	result := Binary2uint(input)
	if result != expected {
		t.Errorf("Failed to convert binary to uint, got %d instead of %d", result, expected)
	}
}

func TestNewIterator(t *testing.T) {
	packet := SeadPacket{
		Type:      'T',
		Location:  'F',
		Timestamp: time.Unix(300, 0),
		Period:    time.Hour + time.Second,
		Count:     5,
		Data:      []int16{3, 5, 7, 11, 13},
		Serial:    555,
	}

	tests := []struct {
		point *decoders.DataPoint
		err   error
	}{
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   3,
				Time:   time.Unix(300, 0),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   5,
				Time:   time.Unix(3901, 0),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   7,
				Time:   time.Unix(7502, 0),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   11,
				Time:   time.Unix(11103, 0),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   13,
				Time:   time.Unix(14704, 0),
			}, nil,
		},
		{
			nil, nil,
		},
		{
			nil, nil,
		},
	}

	iter := NewIterator(packet)

	for i, test := range tests {
		if result, err := iter(); !reflect.DeepEqual(test.point, result) || !errorEqual(test.err, err) {
			t.Errorf("Testing iterator call #%d: got iter() = %v, %v, want = %v, %v", i+1, result, err, test.point, test.err)
		}
	}
}

func TestCompileRegex(t *testing.T) {
	if err := func() (err interface{}) {
		oldHeaderRegexString := headerRegexString
		headerRegexString = "["
		defer func() {
			err = recover()

			headerRegexString = oldHeaderRegexString
			compileRegex()
		}()
		compileRegex()
		return
	}(); !strings.Contains(fmt.Sprintf("%v", err), "regex compile error") {
		t.Error(err)
	}
}
