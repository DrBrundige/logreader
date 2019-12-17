import pandas as pd
# from pandas import ExcelWriter
# from pandas import ExcelFile

from datetime import datetime, timedelta, time
from src.mysqlconnection import connectToMySQL

import csv

print("Log Reader Copyright T. Brundige Jones 2019")


# A number of methods that read Computer lab logs

# read_workbook
# reads a workbook, returning the names of each unique visitor as a list
# Accepts the name of workbook to read.
# Accepts boolean output. If this is true, passes all_names to write_names()
def read_workbook(book_name="lab_log_1912.xlsx", output=False):
	print(f"Reading workbook with name {book_name}")
	all_names = []
	try:
		book = pd.read_excel(book_name, sheet_name=None)
		print("Book read successfully!")
		for sheet_name in book:
			read_sheet(book_name, sheet_name, all_names)
	except Exception as e:
		print("Errant operation")
		print(e)
	else:
		print(f"Complete! Found {len(all_names)} names!")
	finally:
		if output:
			write_names(all_names)
		return all_names


# Reads an individual sheet of a workbook, returning unique names as a list
# Accepts names of book and sheet as strings and existing list of names as reference
# Returns list of names if successful, otherwise returns false
def read_sheet(book_name="lab_log_1912.xlsx", sheet_name="Day01", all_names=[]):
	try:
		sheet = pd.read_excel(book_name, sheet_name=sheet_name)

		if sheet.columns[0] != "Last Name":
			# print("Cell a1 must read 'Last Name'")
			return False

		data = sheet.values
		for row in data:
			name = row[1] + " " + row[0]
			if name not in all_names:
				all_names.append(name)

		return all_names
	except Exception as e:
		print("Errant operation inside Read Sheet!")
		print(e)
		return False


def read_sheet_to_db(book_name="labdb.xlsx", sheet_name="Day01"):
	try:
		sheet = pd.read_excel(book_name, sheet_name=sheet_name)

		assert sheet.columns[0] == "Last Name", "Cell A1 does not contain 'Last Name!' Skipping sheet!"

		# assert len(sheet.columns.array) > 12, "Cell M1 must contain today's date!"
		current_day = sheet.columns.array[12]
		assert isinstance(current_day, datetime), "Cell M1 must contain today's date!"

		data = sheet.values
		successful_rows = 0
		errant_rows = 0
		total_rows = 1
		all_purposes = get_all_purposes()

	except AssertionError as e:
		print(f"Errant operation reading sheet {sheet_name}")
		print(e)
		return -1
	except IndexError as e:
		print(f"Errant operation reading sheet {sheet_name}")
		print("Cell M1 must contain today's date!")
		print(e)
		return -1
	except Exception as e:
		print(f"Unknown error occured reading sheet {sheet_name}")
		print(e)
		return -1

	for row in data:
		try:
			total_rows += 1
			print(f"\nParsing data from row {total_rows}")

			assert isinstance(row[0], str), "Last Name must be must be a string!"
			assert isinstance(row[1], str), "First Name must be must be a string!"
			assert isinstance(row[2], time), "Time In must be time object!"
			assert isinstance(row[3], time), "Time Out must be must be a time object!"
			assert isinstance(row[4], str), "Purpose must be must be a string!"

			user_id = get_user_id(row[1], row[0])
			if user_id == -1:
				print("Invalid user id!")
			else:
				purpose_id = find_purpose_id(all_purposes, row[4])
				time_in = current_day + timedelta(hours=row[2].hour, minutes=row[2].minute)
				time_out = current_day + timedelta(hours=row[3].hour, minutes=row[3].minute)
				span = time_out - time_in
				assert time_in < time_out, "Span must be positive!"

				mysql = connectToMySQL('computer_lab_log')
				columns = "(timein, timeout, span, users_id, purposes_id)"
				query = f"INSERT INTO timeclocks {columns} VALUES (%(i)s, %(o)s, %(s)s,%(u)s,%(p)s)"
				data = {
					"i": time_in,
					"o": time_out,
					"s": span.seconds,
					"u": user_id,
					"p": purpose_id,
				}
				timeclock = mysql.query_db(query, data)
				if timeclock:
					successful_rows += 1
		except AssertionError as e:
			print(f"Errant operation parsing row {total_rows} for sheet {sheet_name}")
			errant_rows += 1
			print(e)
		except Exception as e:
			print(f"Unknown error occurred parsing row {total_rows} for sheet {sheet_name}")
			errant_rows += 1
			print(e)

	print(f"Complete! Added {successful_rows} rows")
	if errant_rows > 0:
		print(f"Errant rows: {errant_rows}")
	return successful_rows


# Attempts to find given user in database
# If it cannot be found, creates user
# Either way returns int representing user id
def get_user_id(first_name, last_name):
	mysql = connectToMySQL('computer_lab_log')

	query = "SELECT * FROM users WHERE first_name=%(f)s AND last_name=%(l)s"
	data = {
		"f": first_name,
		"l": last_name,
	}
	username = mysql.query_db(query, data)
	# if username is emp
	if bool(username):
		# print("Username exists!")
		return username[0]['id']
	else:
		print("Username does not exist! Inserting username!")
		mysql = connectToMySQL('computer_lab_log')

		query = "INSERT INTO users (first_name,last_name) VALUES (%(f)s, %(l)s)"
		data = {
			"f": first_name,
			"l": last_name,
		}
		username = mysql.query_db(query, data)
		if username == False:
			print("Username insertion unsuccessful!")
			return -1
		return username


def get_all_purposes():
	mysql = connectToMySQL('computer_lab_log')
	query = "SELECT id, purpose_name FROM purposes"
	purposes = mysql.query_db(query)
	return purposes


def find_purpose_id(all_purposes, search):
	for purpose in all_purposes:
		if purpose["purpose_name"] == search:
			return purpose["id"]

	# Given search term has not been found. Returns 7, key for the UNKNOWN purpose
	return 7


# Writes contents of enclosed list to csv file
def write_names(output_data):
	print("Writing names")

	try:
		filename = "out" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"

		if __name__ != '__main__':
			filename = 'src/' + filename

		with open(filename, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ')
			print("Preparing to write")
			for name in output_data:
				writer.writerow([name])
	except Exception as e:
		print("Errant operation in Write Names!")
		print(e)
		return False
	else:
		print("Success! Data written to file " + filename)
		return True


if __name__ == '__main__':
	print("Testing Log Reader")
	read_sheet_to_db("labdb.xlsx", "Day02")
# print(get_user_id("Big","Chungus"))
# print(get_user_id("Thicc", "Bih"))
# purposes = get_all_purposes()
# print(find_purpose_id(purposes, "Internet"))
