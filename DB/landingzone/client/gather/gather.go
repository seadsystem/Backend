package gather


import (
	"log"
	"time"

	"golang.org/x/net/context"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)


func GatherData(ctx context.Context, packets []chan *pb.Packet, serial int64, channels_vector []int) {
	// Start on a whole second
	now := time.Now()
	offset := now.Sub(time.Unix(now.Unix(), 0))
	next := now.Add(time.Second).Add(-offset)

loop:
	for {
		offset = next.Sub(time.Now())
		if offset < 0 {
			offset = 0
		}
		select {
		case <-ctx.Done():
			break loop
		case <-time.After(offset):
			data  := gatherData(serial, next, channels_vector)
			for i := 0; i < 8; i++ {
				select {
				case packets[i] <- data[i]:
				default:
					log.Println("Dropping packet for:", next)
				}
		}
		next = next.Add(time.Second)
	}
}
}
