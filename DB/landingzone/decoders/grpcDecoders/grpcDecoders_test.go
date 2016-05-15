package grpcDecoders

import (
	"reflect"
	"testing"
	"time"

	"github.com/golang/protobuf/proto"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"
	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

func TestNewIterator(t *testing.T) {
	packet := &pb.Packet{
		Type:   "T",
		Time:   &pb.Timestamp{300, 0},
		Delta:  int64(time.Hour + time.Second),
		Data:   []int64{3, 5, 7, 11, 13},
		Serial: 555,
		Device: "foo",
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
				Device: proto.String("foo"),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   5,
				Time:   time.Unix(3901, 0),
				Device: proto.String("foo"),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   7,
				Time:   time.Unix(7502, 0),
				Device: proto.String("foo"),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   11,
				Time:   time.Unix(11103, 0),
				Device: proto.String("foo"),
			}, nil,
		},
		{
			&decoders.DataPoint{
				Serial: 555,
				Type:   'T',
				Data:   13,
				Time:   time.Unix(14704, 0),
				Device: proto.String("foo"),
			}, nil,
		},
		{
			nil, nil,
		},
		{
			nil, nil,
		},
	}

	iter, err := NewIterator(packet)
	if err != nil {
		t.Fatal("got NewIterator(packet) = %v, want = nil", err)
	}

	for i, test := range tests {
		if result, err := iter(); !reflect.DeepEqual(test.point, result) || !reflect.DeepEqual(test.err, err) {
			t.Errorf("Testing iterator call #%d: got iter() = %+v, %v, want = %+v, %v", i+1, result, err, test.point, test.err)
		}
	}
}

func TestNewIteratorError(t *testing.T) {
	for _, test := range []struct {
		name string
		in   *pb.Packet
		err  error
	}{
		{"nil packet", nil, NillPacket},
		{"nil Time", &pb.Packet{}, NillPacket},
		{"too short type", &pb.Packet{Time: &pb.Timestamp{}}, InvalidType},
		{"too long type", &pb.Packet{Type: "fo", Time: &pb.Timestamp{}}, InvalidType},
	} {
		if _, err := NewIterator(test.in); err != test.err {
			t.Errorf("%s: got NewIterator(%+v) = _, %v, want = _, %v", test.name, test.in, err, nil, test.err)
		}
	}
}
