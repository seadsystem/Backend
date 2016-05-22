// +build !arm

package gather

import (
	"time"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

const rate = 19000

func gatherData(serial int64, next time.Time) *pb.Packet {
	return &pb.Packet{
		Serial: serial,
		Time:   &pb.Timestamp{next.Unix(), int32(next.Nanosecond())},
		Delta:  int64(time.Second / rate),
		Type:   "P",
		Device: "fake",
		Data:   make([]int64, rate),
	}
}
