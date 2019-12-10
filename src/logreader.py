import pandas as pd
# from pandas import ExcelWriter
# from pandas import ExcelFile

from datetime import datetime
import csv


# A number of methods that read Computer lab logs

# read_workbook
# reads a workbook, returning the names of each unique visitor as a list
# Accepts the name of workbook to read.
# Accepts boolean output. If this is true, passes all_names to write_names()
def read_workbook(book_name="lab_log_1912.xlsx", output=False):
	all_names = []
	try:
		book = pd.read_excel(book_name, sheet_name=None)
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
	print("Log Reader Copyright T. Brundige Jones 2019")
	# print(read_sheet("Total"))
	# print(read_sheet())
	all_names = read_workbook("lab_log_1912.xlsx", True)
	print(all_names)
# write_names(all_names)
