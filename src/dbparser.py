from datetime import datetime, timedelta, time
from src.mysqlconnection import connectToMySQL
from src.logreader import get_all_purposes
# from time import sleep
import csv

print("Database Parser Copyright T. Brundige Jones 2020")


# A number of methods that interact with the computer lab database including exporting data to CSV

# Returns an immutable multidict of timecard objects
# Accepts start and end times as datetime objects or strings
def get_range(start_time, end_time):
	try:
		mysql = connectToMySQL('computer_lab_log')
		query = "SELECT timeclocks.id, users.id as 'user_id', users.first_name, users.last_name,"
		query += " timein, timeout, span, timeclocks.purposes_id as 'purpose_id', purposes.purpose_name\n"
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


# Returns data relating to lab usage by purpose.
#   Including such data as visits, unique visits, and total time
def get_hours_by_purpose(timecards):
	purposes = get_all_purposes()
	data = []
	for purpose in purposes:
		row = {"name": purpose["purpose_name"], "visits": 0, "unique_clients": [], "total_time": 0}
		data.append(row.copy())

	total = {"name": "total", "visits": 0, "unique_clients": [], "total_time": 0}

	for timecard in timecards:
		id = timecard["purpose_id"] - 1
		data[id]["visits"] = data[id]["visits"] + 1
		data[id]["total_time"] = data[id]["total_time"] + timecard["span"]
		if timecard["user_id"] not in data[id]["unique_clients"]:
			data[id]["unique_clients"].append(timecard["user_id"])

		total["visits"] = total["visits"] + 1
		total["total_time"] = total["total_time"] + timecard["span"]
		if timecard["user_id"] not in total["unique_clients"]:
			total["unique_clients"].append(timecard["user_id"])

	data.append(total)
	# converts data into final form
	for row in data:
		row["total_time"] = row["total_time"] / 3600
		row["unique_clients"] = len(row["unique_clients"])

	return data


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
def write_stacked_clients(clients, start="", end="", purpose=""):
	try:
		assert isinstance(clients, dict), "Errant input! Clients must be a dictionary!"
	except AssertionError as e:
		print(e)
		return False

	try:
		filename = "out" + datetime.now().strftime("%Y%m%d-%H%M%S")
		if purpose != "":
			filename += "_" + purpose
		filename += ".csv"

		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')
			headers = ["Name", "Total seconds", "Total time"]
			if start != "" and end != "":
				headers.append(f"Span: {start} - {end}")
			headers.append(purpose)
			writer.writerow(headers)
			total_clients = 0
			total_time = 0

			for key, value in clients.items():
				writer.writerow([key, value, (value / 3600 / 24)])
				total_clients += 1
				total_time += value

			writer.writerow([])
			writer.writerow(["Total:"])
			writer.writerow([total_clients, total_time, (total_time / 3600 / 24)])

	except Exception as e:
		print("Errant operation writing stacked clients!")
		print(e)
		return False
	else:
		print(f"Success! Clients written to file {filename}")
		return True


# Accepts a list of dictionaries
# Outputs data to CSV file
# Returns boolean based on whether the operation succeeded
def write_data(data, start="", end="", purpose=""):
	# assert that data is a list of dictionaries
	# assert that data has rows
	filename = "out" + datetime.now().strftime("%Y%m%d-%H%M%S")
	if purpose != "":
		filename += "_" + purpose
	filename += ".csv"

	try:
		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')
			# writes headers of first row to top of file
			headers = []
			for key, value in data[0].items():
				headers.append(key)
			if start:
				headers.append(f"Time: {start} - {end}")
			if purpose:
				headers.append(purpose)
			writer.writerow(headers)

			# For each row in data, writes values to file
			for row in data:
				values = []
				for key, value in row.items():
					values.append(value)
				writer.writerow(values)
	except Exception as e:
		print("Errant operation writing data!")
		print(e)
		return False
	else:
		print(f"Success! Data written to file {filename}")
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
	print(write_stacked_clients(clients, start, end, "uc"))

	purpose = get_hours_by_purpose(timecards)
	# sleep(1)
	print(write_data(purpose, start, end, "tc"))


if __name__ == '__main__':
	# run_report("2019-12-06", "2020-01-06")
	start = "2019-12-03"
	end = "2020-01-11"
	run_report(start, end)
# timecards = get_range(start, end)
# data = get_hours_by_purpose(timecards)
# write_data(data, start, end, "purposes")
