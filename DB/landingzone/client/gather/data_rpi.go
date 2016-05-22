// +build arm

package gather

// #include "spi.h"
import "C"

import (
	"time"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

const rate = 19000

func gatherData(serial int64, next time.Time) *pb.Packet {
	s := C.sample_data(3)
	return &pb.Packet{
		Serial: serial,
		Time:   &pb.Timestamp{next.Unix(), int32(next.Nanosecond())},
		Delta:  int64(time.Second / rate),
		Type:   "P",
		Device: "fake",
		Data:   []int64{int64(s.first), int64(s.second), int64(s.third)},
	}
}
