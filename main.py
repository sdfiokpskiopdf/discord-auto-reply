import discord
import time
import datetime
import tkinter as tk
import threading
import sys
import os
import json


def in_between(now, start_, end):
	if start_ <= end:
		return start_ <= now < end
	else:
		return start_ <= now or now < end


class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged on as', self.user)
		self.ended = False

	def send_info(self, start, end, message):
		self.startt = int(start.replace(":", ""))
		self.end = int(end.replace(":", ""))
		self.message = message

	def stop(self):
		self.ended = True

	async def on_message(self, message):
		current_time = int(time.strftime('%H%M'))

		if self.ended:
			await client.logout()

		if message.author == self.user:
			return

		if in_between(current_time, self.startt, self.end):
			if isinstance(message.channel, discord.channel.DMChannel):
				await message.channel.send(self.message)
			else:
				for mention in message.mentions:
					if mention.name == self.user.display_name:
						await message.reply(self.message)
						break

	def __del__(self):
		print("logged out")


class MainApplication(tk.Frame):
	def __init__(self, master=None, **kwargs):
		super().__init__(master, **kwargs)
		self.firstRun = True
		tk.Grid.rowconfigure(self, 0, weight=1)
		tk.Grid.rowconfigure(self, 1, weight=1)
		tk.Grid.rowconfigure(self, 2, weight=1)
		tk.Grid.rowconfigure(self, 3, weight=1)
		tk.Grid.rowconfigure(self, 4, weight=1)
		tk.Grid.columnconfigure(self, 0, weight=1)
		tk.Grid.columnconfigure(self, 1, weight=1)

		self.times = []
		self.startt = "00:00"
		self.end = "23:30"
		self.delta = datetime.timedelta(minutes=30)
		self.startt = datetime.datetime.strptime(self.startt, '%H:%M')
		self.end = datetime.datetime.strptime(self.end, '%H:%M')
		self.t = self.startt
		while self.t <= self.end:
			self.times.append(datetime.datetime.strftime(self.t, '%H:%M'))
			self.t += self.delta

		self.tokenStorage = tk.StringVar()
		self.startStorage = tk.StringVar()
		self.endStorage = tk.StringVar()
		self.messageStorage = tk.StringVar()

		self.startStorage.set(self.times[0])
		self.endStorage.set(self.times[-1])

		tk.Label(self, text="Token:", anchor="w").grid(row=0, column=0, sticky="we")
		tk.Entry(self, textvariable=self.tokenStorage).grid(row=0, column=1, sticky="we")
		tk.Label(self, text="Start:", anchor="w").grid(row=1, column=0, sticky="we")
		tk.Label(self, text="End:", anchor="w").grid(row=1, column=1, sticky="we")
		tk.OptionMenu(self, self.startStorage, *self.times).grid(row=2, column=0, sticky="we")
		tk.OptionMenu(self, self.endStorage, *self.times).grid(row=2, column=1, sticky="we")
		tk.Label(self, text="Message:", anchor="w").grid(row=3, column=0, sticky="we")
		tk.Entry(self, textvariable=self.messageStorage).grid(row=3, column=1, sticky="we")
		tk.Button(self, text="Start", command=lambda: self.control_thread()).grid(row=4, column=0, sticky="we")
		tk.Button(self, text="End", command=lambda: self.stop_thread()).grid(row=4, column=1, sticky="we")

		self.load_state()

	def control_thread(self):
		self.s = threading.Thread(target=self.start_thread)
		self.s.start()
		self.save = threading.Thread(target=self.save_state)
		self.save.start()

	def start_thread(self):
		client.send_info(self.startStorage.get(), self.endStorage.get(), self.messageStorage.get())
		client.run(self.tokenStorage.get(), bot=False)

	def stop_thread(self):
		client.stop()
		self.s.join()
		sys.exit()

	def save_state(self):
		data = {}
		data["token"] = self.tokenStorage.get()
		data["start"] = self.startStorage.get()
		data["end"] = self.endStorage.get()
		data["message"] = self.messageStorage.get()
		with open("save.json", "w") as json_file:
			json.dump(data, json_file)

	def load_state(self):
		if os.path.exists("save.json"):
			with open("save.json") as json_file:
				data = json.load(json_file)
				self.tokenStorage.set(data["token"])
				self.startStorage.set(data["start"])
				self.endStorage.set(data["end"])
				self.messageStorage.set(data["message"])
		else:
			open("save.json", "x")


if __name__ == "__main__":
	client = MyClient()
	root = tk.Tk()
	root.title("discord auto reply")
	win = MainApplication(root)
	win.pack(side="top", fill="both", expand=True)
	root.mainloop()
