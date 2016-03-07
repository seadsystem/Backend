/*
 * Package grpcHandlers contains functions to handle grpc connections.
 */
package grpcHandlers

import (
	"log"

	"github.com/golang/protobuf/proto"
	"golang.org/x/net/context"
	"google.golang.org/grpc"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/grpcDecoders"

	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

type server struct {
	db database.DB
}

func (s *server) SendPacket(ctx context.Context, in *pb.Packet) (*pb.Status, error) {
	log.Println("Got grpc request")
	if in != nil {
		log.Printf("Length: %d data points\n", len(in.Data))
	}
	if constants.Verbose {
		log.Printf("Data:\n%s\n", proto.MarshalTextString(in))
	}

	iter, err := grpcDecoders.NewIterator(in)
	if err != nil {
		log.Println("Error creating iterator from packet:", err)
		return &pb.Status{Success: false, Msg: err.Error()}, nil
	}

	if err := s.db.Insert(iter); err != nil {
		log.Println("Error inserting into database:", err)
		return &pb.Status{Success: false, Msg: err.Error()}, nil
	}
	return &pb.Status{Success: true}, nil
}

func Register(s *grpc.Server, db database.DB) {
	pb.RegisterLandingZoneServer(s, &server{db})
}
