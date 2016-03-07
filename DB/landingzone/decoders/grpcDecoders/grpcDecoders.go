package grpcDecoders

import (
	"errors"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

var (
	NillPacket  = errors.New("nill packet")
	InvalidType = errors.New("invalid type: type must be a single character")
)

func NewIterator(packet *pb.Packet) (decoders.Iterator, error) {
	if packet == nil || packet.Time == nil {
		return decoders.NewEmptyIterator(), NillPacket
	}

	if len(packet.Type) != 1 {
		return decoders.NewEmptyIterator(), InvalidType
	}

	next := time.Unix(packet.Time.Seconds, int64(packet.Time.Nanos)) // Set timestamp for first data point to time in packet
	i := 0
	return func() (*decoders.DataPoint, error) {
		if i >= len(packet.Data) {
			// No more data
			return nil, nil
		}

		row := &decoders.DataPoint{
			Serial: packet.Serial,
			Type:   packet.Type[0],
			Data:   packet.Data[i],
			Time:   next,
			Device: &packet.Device,
		}

		i++
		next = next.Add(time.Duration(packet.Delta) * time.Nanosecond) // Add data point time spacing for next data point
		return row, nil
	}, nil
}
