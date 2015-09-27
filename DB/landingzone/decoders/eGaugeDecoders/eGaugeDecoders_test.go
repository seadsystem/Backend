package eGaugeDecoders

import (
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

var (
	deltaData = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="0x1bcd0068">
 <data columns="4" time_stamp="0x555d5148" time_delta="1" delta="true" epoch="0x5503aebc">
  <cname t="P">PowerS</cname>
  <cname t="I">I11</cname>
  <cname t="F">F2</cname>
  <cname t="P">Shed</cname>
  <r><c>100</c><c>200</c><c>-300</c><c>-100</c></r>
  <r><c>1</c><c>0</c><c>-3</c><c>5</c></r>
  <r><c>5</c><c>11</c><c>7</c><c>100</c></r>
 </data>
</group>
 `

	granularityData = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="0x1bcd0067">
 <data columns="1" time_stamp="0x555d5148" time_delta="2" delta="true" epoch="0x5503aebc">
  <cname t="P">Power</cname>
  <r><c>100</c></r>
 </data>
 <data columns="1" time_stamp="0x555d5148" time_delta="1" delta="true" epoch="0x5503aebc">
  <r><c>200</c></r>
 </data>
</group>
 `

	notDeltaData = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="0x1bcd0066">
 <data columns="1" time_stamp="0x555d5148" time_delta="2" delta="false" epoch="0x5503aebc">
  <cname t="P">Power</cname>
  <r><c>100</c></r>
  <r><c>200</c></r>
  <r><c>300</c></r>
 </data>
</group>
 `
)

func TestNewIterator(t *testing.T) {
	tests := []struct {
		xml  string
		name string
		want []*decoders.DataPoint
	}{
		{
			xml:  deltaData,
			name: "delta data",
			want: []*decoders.DataPoint{
				// row 0
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   100,
					Device: stringPtr("PowerS"),
					Time:   time.Unix(0x555d5148, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'I',
					Data:   200,
					Device: stringPtr("I11"),
					Time:   time.Unix(0x555d5148, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'F',
					Data:   -300,
					Device: stringPtr("F2"),
					Time:   time.Unix(0x555d5148, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   -100,
					Device: stringPtr("Shed"),
					Time:   time.Unix(0x555d5148, 0),
				},

				// row 1
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   100 + 1,
					Device: stringPtr("PowerS"),
					Time:   time.Unix(0x555d5148-1, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'I',
					Data:   200 + 0,
					Device: stringPtr("I11"),
					Time:   time.Unix(0x555d5148-1, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'F',
					Data:   -300 - 3,
					Device: stringPtr("F2"),
					Time:   time.Unix(0x555d5148-1, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   -100 + 5,
					Device: stringPtr("Shed"),
					Time:   time.Unix(0x555d5148-1, 0),
				},

				// row 2
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   100 + 1 + 5,
					Device: stringPtr("PowerS"),
					Time:   time.Unix(0x555d5148-2, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'I',
					Data:   200 + 0 + 11,
					Device: stringPtr("I11"),
					Time:   time.Unix(0x555d5148-2, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'F',
					Data:   -300 - 3 + 7,
					Device: stringPtr("F2"),
					Time:   time.Unix(0x555d5148-2, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0068,
					Type:   'P',
					Data:   -100 + 5 + 100,
					Device: stringPtr("Shed"),
					Time:   time.Unix(0x555d5148-2, 0),
				},
				nil,
			},
		},
		{
			xml:  notDeltaData,
			name: "not delta data",
			want: []*decoders.DataPoint{
				&decoders.DataPoint{
					Serial: 0x1bcd0066,
					Type:   'P',
					Data:   100,
					Device: stringPtr("Power"),
					Time:   time.Unix(0x555d5148, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0066,
					Type:   'P',
					Data:   200,
					Device: stringPtr("Power"),
					Time:   time.Unix(0x555d5148-2, 0),
				},
				&decoders.DataPoint{
					Serial: 0x1bcd0066,
					Type:   'P',
					Data:   300,
					Device: stringPtr("Power"),
					Time:   time.Unix(0x555d5148-4, 0),
				},
				nil,
			},
		},
		{
			xml:  granularityData,
			name: "granularity selection with delta data",
			want: []*decoders.DataPoint{
				&decoders.DataPoint{
					Serial: 0x1bcd0067,
					Type:   'P',
					Data:   200,
					Device: stringPtr("Power"),
					Time:   time.Unix(0x555d5148, 0),
				},
			},
		},
	}

	for _, test := range tests {
		packet, err := DecodePacket([]byte(test.xml))
		if err != nil {
			t.Errorf("Decoding packet %s: %v", test.name, err)
			continue
		}
		iter, err := NewIterator(packet)
		if err != nil {
			t.Errorf("Creating iterator for packet %s: %v", test.name, err)
			continue
		}

		for _, want := range test.want {
			if got, err := iter(); !reflect.DeepEqual(got, want) {
				t.Errorf("got iter() = %v, %v, want = %v, nil", got, err, want)
			}
		}
	}
}

func stringPtr(str string) *string {
	return &str
}

func TestNewIteratorErr(t *testing.T) {
	tests := []struct {
		xml  string
		name string
		want string
	}{
		{`<group serial="xxx"></group>`, "invalid serial", "reading serial"},
		{`<group serial="-5"></group>`, "invalid serial", "invalid serial"},
		{`<group serial="5"></group>`, "no data", "no data in packet"},
		{`<group serial="5"><data time_stamp="-5"></data></group>`, "invalid start time", "invalid start time"},
		{`<group serial="5"><data time_stamp="5"><cname t="PP">Power</cname></data></group>`, "invalid column type", "invalid column"},
	}

	for _, test := range tests {
		packet, err := DecodePacket([]byte(test.xml))
		if err != nil {
			t.Errorf("Decoding packet %s: %v", test.name, err)
			continue
		}
		if _, err := NewIterator(packet); err == nil || !strings.HasPrefix(err.Error(), test.want) {
			t.Errorf("Creating iterator for packet with %s: got NewIterator(%s) = %v, want = %s", test.name, test.xml, err, test.want)
		}
	}
}

func TestIteratorErr(t *testing.T) {
	xmls := []string{
		`<group serial="5"><data time_stamp="5"><cname t="P">Power</cname><r><c>4</c><c>6</c></r></data></group>`,
		`<group serial="5"><data time_stamp="5"><cname t="P">Power</cname><r></r></data></group>`,
	}
	want := "invalid row"

	for _, xml := range xmls {
		packet, err := DecodePacket([]byte(xml))
		if err != nil {
			t.Errorf("Decoding packet: %v", err)
			continue
		}
		iter, err := NewIterator(packet)
		if err != nil {
			t.Errorf("Creating iterator: got NewIterator(%s) = %v, want = nil", xml, err)
			continue
		}
		if point, err := iter(); err == nil || !strings.HasPrefix(err.Error(), want) {
			t.Errorf("Error not propagated from iterating over row with mismatched lengths: %s: got iter() = %v, %v, want = nil, %s", xml, point, err, want)
		}
	}
}
