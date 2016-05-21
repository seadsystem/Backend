package endtoend

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	"github.com/seadsystem/Backend/DB/egaugesimulator/transmit"
)

var guestIP string

func TestMain(m *testing.M) {
	flag.Parse()

	cmd := exec.Command("./guestip.sh")
	out, err := cmd.Output()
	if err != nil {
		log.Fatalln("Retrieving guest IP address:", err)
	}
	if len(out) > 1 {
		out = out[:len(out)-1]
	}
	guestIP = string(out)
	log.Println("Guest IP address:", guestIP)

	if err := exec.Command("./cleardb.sh").Run(); err != nil {
		log.Fatalln("Clearing database:", err)
	}

	if err := m.Run(); err != 0 {
		os.Exit(err)
	}
}

func clearDB(t *testing.T) {
	out, err := exec.Command("./cleardb.sh").Output()
	if err != nil {
		t.Fatal("Clearing database:", err)
	}
	t.Log(string(out))
}

func queryAPI(query string) (string, error) {
	resp, err := http.Get(fmt.Sprintf("http://%s:8080/%s", guestIP, query))
	if err != nil {
		return "", fmt.Errorf("making API call: %v", err)
	}
	defer resp.Body.Close()
	buf := new(bytes.Buffer)
	buf.ReadFrom(resp.Body)
	return string(buf.Bytes()), nil
}

func TestAPIUsageMessage(t *testing.T) {
	resp, err := queryAPI("")
	if err != nil || !strings.HasPrefix(resp, "Usage:") {
		t.Errorf("Got queryAPI(\"\") = %q, %v\nWant = \"Usage:...\", <nil>", resp, err)
	}
}

func TestEGauge(t *testing.T) {
	defer clearDB(t)
	rand.Seed(1)

	want := `[["time", "I", "W", "V", "T"],["1970-01-01 00:09:15", "1298498081", "2019727887", "1427131847", "None"],["1970-01-01 00:09:14", "2238482140", "2931629968", "2902073165", "None"],["1970-01-01 00:09:13", "2379436565", "3267752508", "3110313621", "None"],["1970-01-01 00:09:12", "3025639865", "4374163202", "4857592132", "None"],["1970-01-01 00:09:11", "3485768027", "5191618291", "5540616860", "None"],["1970-01-01 00:09:10", "4492701301", "5799429502", "6170048305", "None"],["1970-01-01 00:09:09", "5951024538", "6268768608", "6606388800", "None"],["1970-01-01 00:09:08", "6725990004", "7494280136", "8458575058", "None"],["1970-01-01 00:09:07", "7355448051", "8132260083", "10074713345", "None"],["1970-01-01 00:09:06", "7799080939", "9990552873", "11570906360", "None"],["1970-01-01 00:09:05", "8923976480", "10051333281", "11910913747", "None"],["1970-01-01 00:09:04", "10228043311", "12145648710", "12081539103", "None"],["1970-01-01 00:09:03", "11505385048", "12272609341", "13567650588", "None"],["1970-01-01 00:09:02", "12152900074", "12644695754", "14729653678", "None"],["1970-01-01 00:09:01", "13321465268", "13242786317", "15638366111", "None"],["1970-01-01 00:09:00", "14460889415", "13787260395", "16244130435", "None"],["1970-01-01 00:08:59", "16154405574", "14564231748", "18135082392", "None"],["1970-01-01 00:08:58", "16792449295", "16484858937", "18344364591", "None"],["1970-01-01 00:08:57", "18890362295", "16644397642", "18821727479", "None"],["1970-01-01 00:08:56", "20352966833", "17163047345", "19490716834", "None"],["1970-01-01 00:08:55", "22356239284", "18756155855", "21210969439", "None"],["1970-01-01 00:08:54", "23924399440", "19148984121", "22130859267", "None"],["1970-01-01 00:08:53", "25850675001", "20614971323", "24233094050", "None"],["1970-01-01 00:08:52", "27831110747", "20810042886", "25292108426", "None"],["1970-01-01 00:08:51", "29821799749", "22860772604", "26039333873", "None"],["1970-01-01 00:08:50", "31305364843", "24387434181", "27250041336", "None"],["1970-01-01 00:08:49", "32700132839", "25572340601", "28873159959", "None"],["1970-01-01 00:08:48", "33567293792", "25852911738", "30990503092", "None"],["1970-01-01 00:08:47", "35492173033", "26544581797", "32539156125", "None"],["1970-01-01 00:08:46", "36876311676", "26728235688", "33977058127", "None"],["1970-01-01 00:08:45", "38213610554", "27522145024", "34485630673", "None"],["1970-01-01 00:08:44", "39363119661", "27924252964", "34998537176", "None"],["1970-01-01 00:08:43", "40711950213", "28196452807", "35602689381", "None"],["1970-01-01 00:08:42", "41593111811", "29130420232", "36945070732", "None"],["1970-01-01 00:08:41", "42774543326", "30469609989", "38510974419", "None"],["1970-01-01 00:08:40", "44558101336", "30470713399", "40091669704", "None"],["1970-01-01 00:08:39", "45417059926", "31539877031", "41388702802", "None"],["1970-01-01 00:08:38", "46296708479", "31603595622", "41392791384", "None"],["1970-01-01 00:08:37", "46302813863", "33570306919", "42659450651", "None"],["1970-01-01 00:08:36", "47504100000", "35321376190", "44544966545", "None"],["1970-01-01 00:08:35", "48488597726", "36610221992", "44601370526", "None"],["1970-01-01 00:08:34", "50305009805", "37146434058", "45979591796", "None"],["1970-01-01 00:08:33", "50836440298", "37519357144", "47252241615", "None"],["1970-01-01 00:08:32", "52585339279", "39009363196", "47317358790", "None"],["1970-01-01 00:08:31", "53743284164", "41104608906", "48929610177", "None"],["1970-01-01 00:08:30", "54374657913", "42722010434", "49253802995", "None"],["1970-01-01 00:08:29", "55138662297", "44508568337", "49751654219", "None"],["1970-01-01 00:08:28", "56486926844", "45578861949", "49944575751", "None"],["1970-01-01 00:08:27", "56541030460", "46421139788", "51210266291", "None"],["1970-01-01 00:08:26", "58537356246", "47649686839", "52474224367", "None"],["1970-01-01 00:08:25", "59421609886", "48836344190", "53529943211", "None"],["1970-01-01 00:08:24", "61478800250", "50548336495", "53760542394", "None"],["1970-01-01 00:08:23", "63160355051", "51392836585", "54040603996", "None"],["1970-01-01 00:08:22", "63568447309", "52981600352", "55445147227", "None"],["1970-01-01 00:08:21", "63779724887", "54099108506", "55659315049", "None"],["1970-01-01 00:08:20", "64105806110", "54262725848", "56336219257", "None"],["1970-01-01 00:08:19", "64448653853", "54558657816", "57029020423", "None"],["1970-01-01 00:08:18", "65606307563", "55784552351", "58130210863", "None"],["1970-01-01 00:08:17", "67075562467", "57186945513", "59256565520", "None"],["1970-01-01 00:08:16", "68480596882", "58725334884", "60623748559", "None"],["1970-01-01 00:08:15", "68508140312", "58791224397", "60834268259", "None"],["1970-01-01 00:08:14", "69300801671", "60566021117", "61580909042", "None"]]`

	if err := transmit.Transmit("http://"+guestIP+":9002/", 3, 555, 7, time.Second/2); err != nil {
		t.Fatal("Error transmitting data to eGauge:", err)
	}
	if resp, err := queryAPI("3"); err != nil || resp != want {
		t.Errorf("Got queryAPI(\"3\") = %s, %v\n\nWant = %s, %v\n\n", resp, err, want, nil)
	}
}
