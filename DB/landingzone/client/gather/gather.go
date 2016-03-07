package gather

import (
	"log"
	"time"

	"golang.org/x/net/context"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

const rate = 19000

func GatherData(ctx context.Context, c chan<- *pb.Packet, serial int64) {
	// Start on a whole second
	now := time.Now()
	offset := now.Sub(time.Unix(now.Unix(), 0))
	next := now.Add(time.Second).Add(-offset)

loop:
	for {
		offset := next.Sub(time.Now())
		if offset < 0 {
			offset = 0
		}
		select {
		case <-ctx.Done():
			break loop
		case <-time.After(offset):
			select {
			case c <- &pb.Packet{
				Serial: serial,
				Time:   &pb.Timestamp{next.Unix(), int32(next.Nanosecond())},
				Delta:  int64(time.Second / rate),
				Type:   "P",
				Device: "fake",
				Data:   make([]int64, rate),
			}:
			default:
				log.Println("Dropping packet for:", next)
			}
		}
		next = next.Add(time.Second)
	}
}
