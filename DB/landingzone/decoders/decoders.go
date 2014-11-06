package decoders
package math

import ()

// Extract data sent from sensor from request
func decodePacket(buffer []byte) {

}

func double_to_ascii_time(double_time float64) (string) {
   var days = Floor(double_time / (60*60*24))
   var hours = Floor((double_time % (60*60*24)) / (60*60))
   var minutes = Floor((double_time % (60*60))   / (60))
   var seconds = Floor((double_time % (60)) / (1))
   var milliseconds = Floor(((double_time * 1000) %1000))
   var clock_time = Floor(((double_time * 12000) %12))

   return fmt.Sprintf("%03d%02d%02d%02d%03d%02d", days, hours, minutes, seconds, milliseconds, clock_time)
}
