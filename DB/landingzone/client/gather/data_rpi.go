// +build arm

package gather

// #cgo CFLAGS: -std=c11
// #cgo LDFLAGS: -lrt -lm -ldl -lgsl -lgslcblas -lbcm2835 
// #include "fft_analysis.h"
import "C"

import (
	"math"
	"time"
	"log"
	"fmt"
	pb "github.com/seadsystem/Backend/DB/landingzone/proto/packet"
)

const rate = 19000
const numberOfChannels = 8
const numberOfHarmonics = 50
var previousHarmonics = make([]int64,8)

func convertToCInt(channels_vector []int) []C.int {
	c_channels_vector := make([]C.int, numberOfChannels, numberOfChannels)
	for i := 0; i < numberOfChannels; i++ {
		c_channels_vector[i] = C.int(channels_vector[i]);
	}
	return c_channels_vector
}

func getData(channels_vector []C.int) [][]int64 {
	s := C.sample_harmonics(&channels_vector[0]);
	// allocate composed 2d array
	data := make([][]int64, numberOfChannels)
	for i := range data {
		data[i] = make([]int64, numberOfHarmonics)
	}

	for i := 0; i < numberOfChannels; i++ { 
		if channels_vector[i] == 1 {
			for j := i*numberOfHarmonics; j < i*numberOfHarmonics + numberOfHarmonics; j++ {
				log.Println("packaging harmonics", j)
				log.Println("for channel", i)
				data[i][j - i*50] = int64(s.harmonics[j]); 
			}
		}
	}
	C.deallocate(s);
	return data
}


func gatherData(serial int64, next time.Time, channels_vector []int) []*pb.Packet {
	packets := make([] *pb.Packet, 8)
	
	data := getData(convertToCInt(channels_vector))

	for i := 0; i < numberOfChannels; i++ {
		if channels_vector[i] != 0 {
			if math.Abs(float64(previousHarmonics[i] - data[i][0])) > float64(0.1)*float64(previousHarmonics[i]) {
				previousHarmonics[i] = data[i][0]
				device := fmt.Sprintf("CH%d",i) 
				log.Println("packet ready" + device, i)
				packets[i] = &pb.Packet{
					Serial: serial,
					Time:   &pb.Timestamp{next.Unix(), int32(next.Nanosecond())},
					Delta:  int64(time.Second / rate),
					Type:   "P",
					Device: device,
					Data: data[i],
				}
			}
		}
	}

	return packets
}
