CREATE UNIQUE INDEX idx_client_name
ON users(first_name,last_name);
CREATE UNIQUE INDEX unique_timestamp
ON computer_lab_log.timeclocks (timein ASC, users_id ASC) VISIBLE;
