package grpcHandlers

import (
	"reflect"
	"testing"
	"time"

	"github.com/golang/protobuf/proto"
	"golang.org/x/net/context"
	"google.golang.org/grpc"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/decoders/grpcDecoders"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

func TestHandle(t *testing.T) {
	ctx := context.Background()

	db, mock, err := database.NewMock()
	if err != nil {
		t.Fatalf("Creating mock DB: %v", err)
	}

	mock.ExpectBegin()
	query := "COPY \\\"data_raw\\\" \\(\\\"serial\\\", \\\"type\\\", \\\"data\\\", \\\"time\\\", \\\"device\\\"\\) FROM STDIN"
	stmt := mock.ExpectPrepare(query)
	stmt.ExpectExec().WithArgs(64, "T", 0, time.Unix(500, 0), "fooo").WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WithArgs(64, "T", 1, time.Unix(501, 0), "fooo").WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WithArgs(64, "T", 2, time.Unix(502, 0), "fooo").WillReturnResult(sqlmock.NewResult(0, 1))
	stmt.ExpectExec().WillReturnResult(sqlmock.NewResult(0, 0))
	mock.ExpectCommit()

	in := &pb.Packet{
		Serial: 64,
		Time:   &pb.Timestamp{Seconds: 500},
		Delta:  int64(time.Second),
		Type:   "T",
		Device: "fooo",
		Data:   []int64{0, 1, 2},
	}
	wantStatus := &pb.Status{Success: true}

	s := &server{db}
	if status, err := s.SendPacket(ctx, in); err != nil || !proto.Equal(status, wantStatus) {
		t.Errorf(
			"got s.SendPacket(ctx, %s) = %s, %v, want = %s, %v",
			proto.MarshalTextString(in),
			proto.MarshalTextString(status),
			err,
			proto.MarshalTextString(wantStatus),
			nil,
		)
	}

	if err := mock.ExpectationsWereMet(); err != nil {
		t.Error("mock expectations were not met")
	}
}

func TestHandleError(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name   string
		in     *pb.Packet
		status *pb.Status
		err    error
	}{
		{"nil packet", nil, &pb.Status{Success: false, Msg: grpcDecoders.NillPacket.Error()}, nil},
		{"nil Time", &pb.Packet{}, &pb.Status{Success: false, Msg: grpcDecoders.NillPacket.Error()}, nil},
		{"too short type", &pb.Packet{Time: &pb.Timestamp{}}, &pb.Status{Success: false, Msg: grpcDecoders.InvalidType.Error()}, nil},
		{"too long type", &pb.Packet{Type: "fo", Time: &pb.Timestamp{}}, &pb.Status{Success: false, Msg: grpcDecoders.InvalidType.Error()}, nil},
		{"?", &pb.Packet{Type: "T", Time: &pb.Timestamp{}}, &pb.Status{Success: false, Msg: "call to database transaction Begin, was not expected, next expectation is: ExpectedClose => expecting database Close"}, nil},
	}
	for _, test := range tests {
		db, mock, err := database.NewMock()
		if err != nil {
			t.Fatalf("Creating mock DB: %v", err)
		}
		mock.ExpectClose()

		s := &server{db}
		if status, err := s.SendPacket(ctx, test.in); !reflect.DeepEqual(err, test.err) || !proto.Equal(status, test.status) {
			t.Errorf(
				"%s: got SendPacket(ctx, %s) = %s, %v, want = %s, %v",
				test.name,
				proto.MarshalTextString(test.in),
				proto.MarshalTextString(status),
				err,
				proto.MarshalTextString(test.status),
				test.err,
			)
		}

		if err := db.Close(); err != nil {
			t.Errorf("%s: got db.Close() = %v, want = nil", test.name, err)
		}
	}
}

func TestRegister(t *testing.T) {
	db, mock, err := database.NewMock()
	if err != nil {
		t.Fatalf("Creating mock DB: %v", err)
	}
	mock.ExpectClose()

	s := grpc.NewServer()
	Register(s, db)

	s.Stop()

	if err := db.Close(); err != nil {
		t.Fatalf("got db.Close() = %v, want = nil", err)
	}
}

func TestHandleVerbose(t *testing.T) {
	oldVerbosity := constants.Verbose
	constants.Verbose = true
	defer func() { constants.Verbose = oldVerbosity }()

	t.Log("TestHandle")
	TestHandle(t)

	t.Log("TestHandleError")
	TestHandleError(t)

	t.Log("TestRegister")
	TestRegister(t)
}
