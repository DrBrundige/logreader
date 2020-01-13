import src.dbparser as dbparser
import src.logreader as logreader

import tkinter as tk


class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.report_button = tk.Button(self)
		self.report_button["text"] = "Run Report"
		self.report_button["command"] = self.run_report
		self.report_button.pack(side="top")

		self.read_button = tk.Button(self)
		self.read_button["text"] = "Read Workbook"
		self.read_button["command"] = self.read_workbook
		self.read_button.pack(side="top")

		self.quit = tk.Button(self, text="QUIT", command=self.master.destroy)
		self.quit.pack(side="bottom")

	def run_report(self):
		print("Outputting data to csv")
		dbparser.run_report()

	def read_workbook(self):
		print("Reading workbook")
		logreader.read_workbook_to_db()


root = tk.Tk()
app = Application(master=root)
app.mainloop()
