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
			"16128222828000",
			14012548*time.Second + 280*time.Millisecond,
			nil,
		},
		{
			"16128222828000000",
			0,
			errors.New("invalid ascii time: 16128222828000000"),
		},
		{
			"-1612822282800",
			0,
			errors.New("invalid ascii time: -1612822282800"),
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

func TestDecodeHeader(t *testing.T) {
	tests := []struct {
		packet []byte
		serial int
		offset time.Time
		err    error
	}{
		{[]byte("THS000001t00000132745009X"), 1, time.Now().Add(-func() time.Duration { d, _ := AsciiTimeToDuration([]byte("00000132745009")); return d }()), nil},
		{[]byte{}, 0, time.Time{}, InvalidHeader},
		{[]byte("THS000001t000000132745009X"), 0, time.Time{}, errors.New("invalid ascii time: 000000132745009")},
	}
	for _, test := range tests {
		if serial, offset, err := DecodeHeader(test.packet); serial != test.serial || offset.Sub(test.offset) > time.Second/10 || offset.Sub(test.offset) < -time.Second/10 || !errorEqual(err, test.err) {
			t.Errorf("got DecodeHeader(%s) = %d, %v, %v, want = %d, %v, %v", string(test.packet), serial, offset, err, test.serial, test.offset, test.err)
		}
	}
}

func TestDecodePacket(t *testing.T) {
	tests := []struct {
		raw []byte
		dec SeadPacket
		err error
	}{
		{
			raw: append(append(append([]byte("TIlIt00000134730811P00000000000005C"), []byte{200, 0}...), []byte("D")...),
				[]byte{
					137, 255, 86, 255, 25, 255, 207, 254, 130, 254, 70, 254, 42, 254, 70, 254, 158,
					254, 234, 254, 35, 255, 99, 255, 147, 255, 194, 255, 231, 255, 17, 0, 52, 0, 90, 0,
					127, 0, 184, 0, 254, 0, 82, 1, 137, 1, 182, 1, 215, 1, 151, 1, 90, 1, 3, 1, 192,
					0, 144, 0, 86, 0, 46, 0, 15, 0, 223, 255, 194, 255, 159, 255, 107, 255, 63, 255,
					239, 254, 162, 254, 90, 254, 64, 254, 50, 254, 120, 254, 199, 254, 10, 255, 82,
					255, 130, 255, 186, 255, 221, 255, 0, 0, 42, 0, 78, 0, 114, 0, 154, 0, 206, 0, 42,
					1, 127, 1, 165, 1, 204, 1, 187, 1, 100, 1, 34, 1, 223, 0, 170, 0, 110, 0, 60, 0,
					18, 0, 246, 255, 203, 255, 171, 255, 136, 255, 87, 255, 23, 255, 188, 254, 127,
					254, 74, 254, 55, 254, 82, 254, 169, 254, 248, 254, 46, 255, 109, 255, 155, 255,
					212, 255, 249, 255, 26, 0, 62, 0, 95, 0, 138, 0, 190, 0, 13, 1, 87, 1, 162, 1,
					187, 1, 207, 1, 136, 1, 58, 1, 241, 0, 174, 0, 123, 0, 68, 0, 36, 0, 253, 255,
					223, 255, 186, 255, 143, 255, 106, 255, 31, 255, 219, 254, 138, 254, 90, 254, 58,
					254, 66, 254, 158, 254, 223, 254, 35, 255, 94, 255, 142, 255, 196, 255, 235, 255,
					14, 0, 47, 0, 94, 0, 122, 0, 178, 0, 239, 0, 74, 1, 129, 1, 174, 1, 210, 1, 158, 1,
					84, 1, 251, 0, 194, 0, 148, 0, 82, 0, 44, 0, 3, 0, 230, 255, 186, 255, 153, 255,
					106, 255, 66, 255, 250, 254, 154, 254, 91, 254, 52, 254, 40, 254, 148, 254, 225,
					254, 42, 255, 106, 255, 158, 255, 199, 255, 246, 255, 24, 0, 70, 0, 103, 0, 139, 0,
					207, 0, 28, 1, 106, 1, 174, 1, 198, 1, 175, 1, 98, 1, 10, 1, 198, 0, 147, 0, 91, 0,
					46, 0, 10, 0, 227, 255, 187, 255, 150, 255, 103, 255, 46, 255, 211, 254, 146, 254,
					90, 254, 46, 254, 80, 254, 171, 254, 250, 254, 58, 255, 123, 255, 174, 255, 223,
					255, 6, 0, 34, 0, 74, 0, 115, 0, 155, 0, 218, 0, 42, 1, 127, 1, 170, 1, 200, 1,
					168, 1, 88,
				}...),
			dec: SeadPacket{
				Type:      73,
				Location:  73,
				Timestamp: time.Time{}.Add(func() time.Duration { d, _ := AsciiTimeToDuration([]byte("00000134730811")); return d }()),
				Period:    time.Duration(416.666 * float64(time.Microsecond)),
				Count:     200,
				Data:      []int16{-119, -170, -231, -305, -382, -442, -470, -442, -354, -278, -221, -157, -109, -62, -25, 17, 52, 90, 127, 184, 254, 338, 393, 438, 471, 407, 346, 259, 192, 144, 86, 46, 15, -33, -62, -97, -149, -193, -273, -350, -422, -448, -462, -392, -313, -246, -174, -126, -70, -35, 0, 42, 78, 114, 154, 206, 298, 383, 421, 460, 443, 356, 290, 223, 170, 110, 60, 18, -10, -53, -85, -120, -169, -233, -324, -385, -438, -457, -430, -343, -264, -210, -147, -101, -44, -7, 26, 62, 95, 138, 190, 269, 343, 418, 443, 463, 392, 314, 241, 174, 123, 68, 36, -3, -33, -70, -113, -150, -225, -293, -374, -422, -454, -446, -354, -289, -221, -162, -114, -60, -21, 14, 47, 94, 122, 178, 239, 330, 385, 430, 466, 414, 340, 251, 194, 148, 82, 44, 3, -26, -70, -103, -150, -190, -262, -358, -421, -460, -472, -364, -287, -214, -150, -98, -57, -10, 24, 70, 103, 139, 207, 284, 362, 430, 454, 431, 354, 266, 198, 147, 91, 46, 10, -29, -69, -106, -153, -210, -301, -366, -422, -466, -432, -341, -262, -198, -133, -82, -33, 6, 34, 74, 115, 155, 218, 298, 383, 426, 456, 424},
				Serial:    0,
			},
		},
	}
	for _, test := range tests {
		if packet, err := DecodePacket(test.raw, time.Time{}); !errorEqual(err, test.err) || !reflect.DeepEqual(packet, test.dec) {
			t.Errorf("got = %+v, %v, want = %+v, %v", packet, err, test.dec, err)
		}
	}
}
