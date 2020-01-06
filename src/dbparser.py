import pandas as pd
from datetime import datetime, timedelta, time
from src.mysqlconnection import connectToMySQL
import csv

print("Database Parser Copyright T. Brundige Jones 2020")


# A number of methods that interact with the computer lab database including exporting data to CSV

# Returns an immutable multidict of timecard objects
# Accepts start and end times as datetime objects or strings
def get_range(start_time, end_time):
	try:
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
	except Exception as e:
		print("Errant operation getting range!")
		print(e)
		return {}
	else:
		print(f"Success! {len(timecards)} rows returned!")
		return timecards


# Returns total span of all rows as an integer
# Accepts immutable multidict provided by get_range (required) and purpose string.
#   This is used as a filter
def get_total_time(timecards, purpose=""):
	try:
		total_span = 0
		for row in timecards:
			if purpose == "" or purpose == row["purpose_name"]:
				total_span += row["span"]

	except Exception as e:
		print("Errant operation summing time!")
		print(e)
		return -1
	else:
		return total_span


# Returns dictionary of unique clients and total time span
# Accepts immutable multidict provided by get_range (required) and optional purpose string.
#   This is used as a filter
def stack_clients(timecards, purpose=""):
	try:
		all_names = {}
		for row in timecards:
			# if purpose is set to default, continues
			# Otherwise, filters all clients where purpose is not equal to parameterized value
			if purpose == "" or purpose == row["purpose_name"]:
				name = row["first_name"] + " " + row["last_name"]
				if name not in all_names:
					all_names[name] = row["span"]
				else:
					all_names[name] = all_names[name] + row["span"]
	except Exception as e:
		print("Errant operation stacking clients!")
		print(e)
		return {}
	else:
		print(f"Success! Found {len(all_names)} unique names!")
		return all_names


# Accepts dictionary returned from stack_clients
# Outputs clients to a CSV file
# Returns boolean based on whether the operation succeeded
def write_stacked_clients(clients, start="", end=""):
	try:
		assert isinstance(clients, dict), "Errant input! Clients must be a dictionary!"
	except AssertionError as e:
		print(e)
		return False

	try:
		filename = "out" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"
		if __name__ != '__main__':
			filename = 'src/' + filename

		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')
			# todo: Write timeframe in headers
			if start == " " or end == "":
				writer.writerow(["Name", "Total seconds", "Total time"])
			else:
				writer.writerow(["Name", "Total seconds", "Total time", f"Span: {start} - {end}"])
			for key, value in clients.items():
				writer.writerow([key, value, (value / 3600 / 24)])

	except Exception as e:
		print("Errant operation writing stacked clients!")
		print(e)
		return False
	else:
		print(f"Success! Clients written to file {filename}")
		return True


def run_report(start="", end=""):
	if start == "" or end == "":
		start = datetime.today()
		start = start - timedelta(hours=start.hour)
		start = start - timedelta(minutes=start.minute)
		start = start - timedelta(seconds=start.second)
		start = start - timedelta(microseconds=start.microsecond)
		start = start - timedelta(hours=start.hour)
		end = start + timedelta(hours=24)

	# print(start)
	# print(end)

	timecards = get_range(start, end)
	clients = stack_clients(timecards)
	print(write_stacked_clients(clients, start, end))


if __name__ == '__main__':
	run_report("2019-12-06","2020-01-06")
