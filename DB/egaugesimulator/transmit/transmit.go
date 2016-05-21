package transmit

import (
	"bytes"
	"fmt"
	"math/rand"
	"net/http"
	"text/template"
	"time"
)

var reportTemplate *template.Template

func init() {
	reportTemplate = template.Must(template.New("reportTemplate").Parse(reportTemplateText))
}

func Transmit(url string, serial int, timestamp int64, epoch int64, timeout time.Duration) error {
	client := http.Client{
		Timeout: timeout,
	}

	content := map[string]interface{}{}
	content["epoch"] = epoch
	content["serial"] = serial
	content["timestamp"] = timestamp

	data := [rows][columns]int32{}
	for row := 0; row < rows; row++ {
		for column := 0; column < columns; column++ {
			data[row][column] = rand.Int31()
		}
	}
	content["data"] = data

	buf := bytes.Buffer{}
	reportTemplate.Execute(&buf, content)

	resp, err := client.Post(url, "application/xml", &buf)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		buf := new(bytes.Buffer)
		buf.ReadFrom(resp.Body)
		return fmt.Errorf("HTTP error code %s:\n%s\n", resp.Status, string(buf.Bytes()))
	}
	return nil
}

const (
	rows               = 62
	columns            = 3
	reportTemplateText = `<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE group PUBLIC "-//ESL/DTD eGauge 1.0//EN" "http://www.egauge.net/DTD/egauge-hist.dtd">
<group serial="{{.serial | printf "0x%08x"}}">
<data columns="3" time_stamp="{{.timestamp | printf "0x%08x"}}" time_delta="1" delta="true" epoch="{{.epoch | printf "0x%08x"}}">
 <cname t="I">heater</cname>
 <cname t="W">lamp</cname>
 <cname t="V">lamp+</cname>{{range $row_number, $row := $.data}}
 <r>{{range $col_number, $point := $row}}<c>{{$point}}</c>{{end}}</r>{{end}}
</data>
</group>`
)
