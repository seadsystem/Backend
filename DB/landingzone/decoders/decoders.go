package decoders

import (
	"math"
	"regexp"
	"errors"
	"strconv"
	
	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

var headerRegex *Regexp
var InvalidHeader = errors.New("Invalid header.")

func init() {
	headerRegex, err := regexp.Compile(constants.HEADER_REGEX)
	if err != nil {
		log.Println("Regex compile error:", err)
	}
}

// Extract data sent from sensor from request
func DecodePacket(buffer []byte) {

}

func DecodeHeader(packet []byte) (serial int, err error) {
	serialString = headerRegex.Find(packet)
	if serialString == nil {
		err = InvalidHeader
		return
	}
	serial, err = strconv.Atoi(string(serialString))
	return
}

func doubleToAsciiTime(double_time float64) (string) {
   var days = math.Floor(double_time / (60*60*24))
   var hours = math.Floor((double_time % (60*60*24)) / (60*60))
   var minutes = math.Floor((double_time % (60*60))   / (60))
   var seconds = math.Floor((double_time % (60)) / (1))
   var milliseconds = math.Floor(((double_time * 1000) %1000))
   var clock_time = math.Floor(((double_time * 12000) %12))

   return fmt.Sprintf("%03d%02d%02d%02d%03d%02d", days, hours, minutes, seconds, milliseconds, clock_time)
}
