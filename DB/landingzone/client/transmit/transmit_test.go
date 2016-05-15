package transmit

import (
	"errors"
	"testing"
	"time"

	"google.golang.org/grpc"

	"golang.org/x/net/context"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

type stubLandingZoneClient struct {
	data  []*pb.Packet
	resp  *pb.Status
	err   error
	delay time.Duration
}

func (s *stubLandingZoneClient) SendPacket(ctx context.Context, in *pb.Packet, opts ...grpc.CallOption) (*pb.Status, error) {
	select {
	case <-ctx.Done():
	case <-time.After(s.delay):
	}
	s.data = append(s.data, in)
	return s.resp, s.err
}

func TestTransmitCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	c := make(chan *pb.Packet)
	client := &stubLandingZoneClient{}
	done := make(chan struct{}, 1)
	go func() {
		Transmit(ctx, client, c, time.Second/4)
		done <- struct{}{}
	}()
	select {
	case <-done:
	case <-time.After(time.Second / 8):
		t.Error("GatherData timed out")
	}
}

func TestTransmitDelayedCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet)
	client := &stubLandingZoneClient{delay: time.Second, resp: &pb.Status{}}
	done := make(chan struct{}, 1)
	go func() {
		Transmit(ctx, client, c, time.Second)
		done <- struct{}{}
	}()
	select {
	case c <- &pb.Packet{}:
	case <-time.After(time.Second / 2):
		t.Error("sending data timed out")
	}
	time.Sleep(time.Second / 4)
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second / 2):
		t.Error("GatherData timed out")
	}
}

func TestTransmit(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet)
	client := &stubLandingZoneClient{resp: &pb.Status{}}
	done := make(chan struct{}, 1)
	go func() {
		Transmit(ctx, client, c, time.Second)
		done <- struct{}{}
	}()
	select {
	case c <- &pb.Packet{}:
	case <-time.After(time.Second / 4):
		t.Error("sending data timed out")
	}
	time.Sleep(time.Second / 4)
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second / 4):
		t.Error("GatherData timed out")
	}
	if len(client.data) != 1 {
		t.Errorf("Unexpected number of packets received: got = %d, want = 1", len(client.data))
	}
}

func TestTransmitError(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet)
	client := &stubLandingZoneClient{err: errors.New("")}
	done := make(chan struct{}, 1)
	go func() {
		Transmit(ctx, client, c, time.Second)
		done <- struct{}{}
	}()
	select {
	case c <- &pb.Packet{}:
	case <-time.After(time.Second / 4):
		t.Error("sending data timed out")
	}
	time.Sleep(time.Second / 4)
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second / 4):
		t.Error("GatherData timed out")
	}
	if len(client.data) != 1 {
		t.Errorf("Unexpected number of packets received: got = %d, want = 1", len(client.data))
	}
}
