package gather

import (
	"testing"
	"time"

	"golang.org/x/net/context"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

func TestGatherDataCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	c := make(chan *pb.Packet)
	done := make(chan struct{}, 1)
	go func() {
		GatherData(ctx, c, 0)
		done <- struct{}{}
	}()
	select {
	case <-done:
	case <-time.After(time.Second):
		t.Error("GatherData timed out")
	}
}

func TestGatherDataCancel2(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet, 1)
	done := make(chan struct{}, 1)
	go func() {
		GatherData(ctx, c, 0)
		done <- struct{}{}
	}()
	time.Sleep(time.Second)
	cancel()
	select {
	case <-done:
	case <-time.After(2*time.Second):
		t.Error("GatherData timed out")
	}
}

func TestGatherDataDropPacket(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet, 0)
	done := make(chan struct{}, 1)
	go func() {
		GatherData(ctx, c, 0)
		done <- struct{}{}
	}()
	time.Sleep(time.Second)
	cancel()
	select {
	case <-done:
	case <-time.After(2*time.Second):
		t.Error("GatherData timed out")
	}
}

func TestGatherData(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	c := make(chan *pb.Packet, 0)
	done := make(chan struct{}, 1)
	go func() {
		GatherData(ctx, c, 0)
		done <- struct{}{}
	}()
	select {
	case msg := <-c:
		if msg == nil {
			t.Error("got msg = nil, want != nil")
		}
	case <-time.After(2*time.Second):
		t.Error("getting data from GatherData timed out")
	}
	cancel()
	select {
	case <-done:
	case <-time.After(2*time.Second):
		t.Error("GatherData timed out")
	}
}
