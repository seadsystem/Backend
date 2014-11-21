/*
 * Created By: Quintin Leong
 * Created Date: November 5th, 2014
 * File Name: table_stats.sql
 * File Desciption: Creates stats of metric tables produced by create_aggregates.sql script.
 *					Creates a table that host all of the data we collected in sprint #1
 *					along with the metadata associated with each appliance.
 *
 * Output Table(s): scratch.device_stats
 */

CREATE TABLE scratch.device_stats(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_type VARCHAR(30) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type VARCHAR(30) NOT NULL,
	number_data_points INT(10) NOT NULL,
	frequency DOUBLE NOT NULL
);


INSERT INTO scratch.device_stats(device_type, packet_id, sensor_type, number_data_points, frequency);
SELECT 
	"computer" AS 'device_type',
	c.packet_id AS 'packet_id',
	c.sensor_type AS 'sensor_type',
	COUNT(c.`data`) AS 'number_data_points',
	ROUND(AVG(c.frequency),2) AS 'frequency'
FROM scratch.computer c
GROUP BY 1,2,3
UNION
SELECT 
	"lamp" AS 'device_type',
	l.packet_id AS 'packet_id',
	l.sensor_type AS 'sensor_type',
	COUNT(l.`data`) AS 'number_data_points',
	ROUND(AVG(l.frequency),2) AS 'frequency'


FROM scratch.lamp l
GROUP BY 1,2,3
UNION
SELECT 
	"speaker" AS 'device_type',
	s.packet_id AS 'packet_id',
	s.sensor_type AS 'sensor_type',
	COUNT(s.`data`) AS 'number_data_points',
	ROUND(AVG(s.frequency),2) AS 'frequency'


FROM scratch.speaker s
GROUP BY 1,2,3
UNION
SELECT 
	"television" AS 'device_type',
	t.packet_id AS 'packet_id',
	t.sensor_type AS 'sensor_type',
	COUNT(t.`data`) AS 'number_data_points',
	ROUND(AVG(t.frequency),2) AS 'frequency'


FROM scratch.television t
GROUP BY 1,2,3
ORDER BY 1,2,3
;

