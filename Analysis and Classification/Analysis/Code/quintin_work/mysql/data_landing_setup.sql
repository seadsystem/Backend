/*
 * Created By: Quintin Leong
 * Created Date: November 5th, 2014
 * File Name: data_landing_setup.sql
 * File Description: Sets up landing table that will be product of cron migration from shempser.data_raw
 */
CREATE TABLE scratch.data_landing(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_id INT(10) NOT NULL,
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type_id INT(10) NOT NULL,
	sensor_type VARCHAR(50) NOT NULL,
	`data` DOUBLE NOT NULL,
	frequency DOUBLE NOT NULL,
	microstamp BIGINT(20) NOT NULL
);

CREATE INDEX i ON scratch.data_landing(packet_id);
CREATE INDEX j ON scratch.data_landing(sensor_id);
