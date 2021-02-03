import discord
import time
import datetime
import tkinter as tk
import threading
import sys
import os
import csv
import json
import webbrowser
from tkinter.messagebox import showinfo
from tkinter.messagebox import askquestion

def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end


class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged on as', self.user)
		self.ended = False

	def send_info(self, start, end, message):
		self.startt = start
		self.end = end
		self.message = message

	def stop(self):
		self.ended = True

	async def on_message(self, message):
		current_time = time.strftime('%H:%M')

		if self.ended:
			await client.logout()

		if message.author == self.user:
			return

		if in_between(current_time, self.startt, self.end):
			if isinstance(message.channel, discord.channel.DMChannel):
				win.save_message(message.content, message.created_at, message.author, message.jump_url)
				await message.channel.send(self.message)
			else:
				for mention in message.mentions:
					if mention.name == self.user.display_name:
						win.save_message(message.content, message.created_at, message.author, message.jump_url)
						await message.reply(self.message)
						break


class MainApplication(tk.Frame):
	def __init__(self, master=None, **kwargs):
		super().__init__(master, **kwargs)
		self.first_save = True
		self.window_open = False
		self.first = False

		tk.Grid.rowconfigure(self, 0, weight=1)
		tk.Grid.rowconfigure(self, 1, weight=1)
		tk.Grid.rowconfigure(self, 2, weight=1)
		tk.Grid.rowconfigure(self, 3, weight=1)
		tk.Grid.rowconfigure(self, 4, weight=1)
		tk.Grid.rowconfigure(self, 5, weight=1)
		tk.Grid.columnconfigure(self, 0, weight=1)
		tk.Grid.columnconfigure(self, 1, weight=1)

		self.times = self.get_times_list()

		self.tokenStorage = tk.StringVar()
		self.startStorage = tk.StringVar()
		self.endStorage = tk.StringVar()
		self.messageStorage = tk.StringVar()

		self.startStorage.set(self.times[0])
		self.endStorage.set(self.times[-1])

		tk.Label(self, relief="sunken", text="Token:", anchor="w").grid(row=0, column=0, sticky="we")
		tk.Entry(self, relief="sunken", textvariable=self.tokenStorage).grid(row=0, column=1, sticky="we")
		tk.Label(self, relief="sunken", text="Start:", anchor="w").grid(row=1, column=0, sticky="we")
		tk.Label(self, relief="sunken", text="End:", anchor="w").grid(row=1, column=1, sticky="we")
		tk.OptionMenu(self, self.startStorage, *self.times).grid(row=2, column=0, sticky="we")
		tk.OptionMenu(self, self.endStorage, *self.times).grid(row=2, column=1, sticky="we")
		tk.Label(self, relief="sunken", text="Message:", anchor="w").grid(row=3, column=0, sticky="we")
		tk.Entry(self, relief="sunken", textvariable=self.messageStorage).grid(row=3, column=1, sticky="we")
		tk.Button(self, text="Start", command=lambda: self.control_thread()).grid(row=4, column=0, sticky="we")
		tk.Button(self, text="End", command=lambda: self.stop_thread()).grid(row=4, column=1, sticky="we")
		tk.Button(self, text="History", command=lambda: self.create_window()).grid(row=5, column=0, columnspan=2, sticky="we")

		self.load_state()
		self.history_data = self.load_messages()

	def create_window(self):
		#shitty programming starts here

		if self.window_open:
			self.window_open = False
			self.window.destroy()
		else:
			self.window_open = True
			self.window = tk.Toplevel()
			self.window.title("History")

			self.history_data = self.load_messages()
			
			if len(self.history_data) == 0:
				tk.Label(self.window, text="No history to show yet.").place(relx=.4, rely=.4)
				return None

			i = 0
			while i <= 3:
				self.window.columnconfigure(i, weight=1)
				i += 1


			i = 0
			for item in self.history_data:

				if i > 10:
					break

				self.window.rowconfigure(i, weight=1)
				tk.Label(self.window, relief="sunken", text=item["time"], anchor="w").grid(row=i, column=0, sticky="we")
				tk.Label(self.window, relief="sunken", text=item["author"], anchor="w").grid(row=i, column=1, sticky="we")
				tk.Label(self.window, relief="sunken", text=item["content"], anchor="w").grid(row=i, column=2, sticky="we")
				tk.Button(self.window, text="Link", command=lambda link=item["link"]: self.open_link(link)).grid(row=i, column=3, sticky="we")

				i += 1
			


	def control_thread(self):
		print("Active Threads:", threading.active_count())
		if threading.active_count() > 1:
			self.popup("Error", "You have already started the program")
		else:
			s = threading.Thread(target=self.start_thread)
			s.daemon = True
			s.start()
		save = threading.Thread(target=self.save_state)
		save.start()

	def start_thread(self):
		client.send_info(self.startStorage.get(), self.endStorage.get(), self.messageStorage.get())
		client.run(self.tokenStorage.get(), bot=False)


	def stop_thread(self):
		result = self.question_popup("Exit", "Are you sure you want to end the program?")
		if result == 'yes':
			print("Logged out as", client.user)
			sys.exit()

	def save_message(self, content, time, author, link):
		with open("history.csv", "a", newline='') as csv_file:
			writer = csv.writer(csv_file)
			line = [str(content), str(time.strftime("%H:%M")), str(author), str(link)]
			writer.writerow(line)
	
	def load_messages(self):
		history_data = []
		if os.path.isfile("history.csv"):
			with open("history.csv", newline='') as csv_file:
				reader = csv.reader(csv_file)
				for row in reversed(list(reader)):

					history_dict = {}
					history_dict["content"] = row[0]
					history_dict["time"] = row[1]
					history_dict["author"] = row[2]
					history_dict["link"] = row[3] 

					history_data.append(history_dict)
		else:
			open("history.csv", "x")

		return history_data

 
	def save_state(self):
		with open("info.csv", "w", newline='') as csv_file:
			writer = csv.writer(csv_file)
			line = [self.tokenStorage.get(), self.startStorage.get(), self.endStorage.get(), self.messageStorage.get()]
			writer.writerow(line)
			

	def load_state(self):
		if os.path.isfile("info.csv"):
			with open("info.csv", newline='') as csv_file:
				reader = csv.reader(csv_file)
				row_one = next(reader)
				self.tokenStorage.set(row_one[0])
				self.startStorage.set(row_one[1])
				self.endStorage.set(row_one[2])
				self.messageStorage.set(row_one[3])
		else:
			open("info.csv", "x")


	def get_times_list(self):
		times = []
		start = "00:00"
		end = "23:30"
		delta = datetime.timedelta(minutes=30)
		start = datetime.datetime.strptime(start, '%H:%M')
		end = datetime.datetime.strptime(end, '%H:%M')
		t = start
		while t <= end:
			times.append(datetime.datetime.strftime(t, '%H:%M'))
			t += delta

		return times

	def open_link(self, link):
		webbrowser.open_new(link)

	def popup(self, title, message):
		showinfo(title, message)

	def question_popup(self, title, message):
		return askquestion(title, message, icon="warning")

if __name__ == "__main__":
	print("Not running in venv:", sys.base_prefix == sys.prefix)
	print("Active threads:", threading.active_count())
	print("Starting...")
	client = MyClient()
	time.sleep(3)
	print("Started")
	root = tk.Tk()
	root.title("discord auto reply")
	root.resizable(width=False, height=False)
	win = MainApplication(root)
	win.pack(side="top", fill="both", expand=True)
	root.mainloop()
