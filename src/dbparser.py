import pandas as pd
from datetime import datetime, timedelta, time
from src.mysqlconnection import connectToMySQL
import csv


# Returns an immutable multidict of timecard objects
def get_range(start_time, end_time):
	mysql = connectToMySQL('computer_lab_log')
	query = "SELECT timeclocks.id, users.first_name, users.last_name, timein, timeout, span, purposes.purpose_name\n"
	query += "FROM computer_lab_log.timeclocks\n"
	query += "JOIN users ON timeclocks.users_id = users.id\n"
	query += "JOIN purposes ON timeclocks.purposes_id = purposes.id\n"
	query += "WHERE timein >= %(i)s AND timeout < %(o)s\n"
	query += "ORDER BY timein"

	data = {
		"i": start_time,
		"o": end_time,
	}
	timecards = mysql.query_db(query, data)
	return timecards


# Returns total span of all rows as an integer
# Accepts immutable multidict provided by get_range (required) and purpose string.
#   This is used as a filter
def get_total_time(timecards, purpose=""):
	total_span = 0
	for row in timecards:
		if purpose == "" or purpose == row["purpose_name"]:
			total_span += row["span"]
	return total_span


# Returns dictionary of unique clients and total time span
# Accepts immutable multidict provided by get_range (required) and purpose string.
#   This is used as a filter
def stack_clients(timecards, purpose=""):
	all_names = {}
	for row in timecards:
		if purpose == "" or purpose == row["purpose_name"]:
			name = row["first_name"] + " " + row["last_name"]
			if name not in all_names:
				all_names[name] = row["span"]
			else:
				all_names[name] = all_names[name] + row["span"]

	return all_names


def write_stacked_clients(clients):
	output = ["Name, Total Time"]
	filename = "out" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"
	if __name__ != '__main__':
		filename = 'src/' + filename

	with open(filename, 'w', newline='') as csvfile:
		print("Preparing to write")
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(["Name", "Total seconds", "Total time"])
		for key, value in clients.items():
			writer.writerow([key, value, (value / 3600 / 24)])
	return True


if __name__ == '__main__':
	start = datetime.today()
	start = start - timedelta(hours=start.hour)
	start = start - timedelta(minutes=start.minute)
	start = start - timedelta(seconds=start.second)
	start = start - timedelta(microseconds=start.microsecond)
	end = start + timedelta(hours=24)
	start = start - timedelta(hours=24)
	timecards = get_range(start, end)
	# print(get_total_time(timecards))
	# print(get_total_time(timecards, "GED"))
	# print(stack_clients(timecards))
	# print(stack_clients(timecards, "GED"))
	clients = stack_clients(timecards)
	print(write_stacked_clients(clients))
