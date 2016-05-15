package transmit

import (
	"log"
	"time"

	"golang.org/x/net/context"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

func Transmit(ctx context.Context, client pb.LandingZoneClient, c <-chan *pb.Packet, timeout time.Duration) {
loop:
	for {
		select {
		case msg := <-c:
			toCtx, _ := context.WithTimeout(ctx, timeout)
			status, err := client.SendPacket(toCtx, msg)
			if err != nil {
				log.Println("Error sending packet:", err)
				continue
			}
			if !status.Success {
				log.Println("SendPacket did not succeed:", status.Msg)
			}
		case <-ctx.Done():
			break loop
		}
	}
}
