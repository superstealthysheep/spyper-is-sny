import discord
from discord.ext import commands, tasks
import random

"""
to do: 
- make bot store separate values (e.g. response dicts, probabilities) for separate guilds
"""

config = {
	"default_accuracy": 10,
	"default_celebration_probability": 25,
	"command_prefix": ".",
	"victory_message_filename": "victory_msgs.csv",
	"csv_delimiter": ",,," #cursed delimiter?
	}

class WeightDict: #A dictionary where all the values are integer weights. A total weight is stored along with the object so you don't have to calculate it every time
	def __init__(self, d): #to be clear, d stands for dictionary
		self.d = d
		self.total_weight = 0

		#self.total_weight is set to be the total of all of the weights in the dict
		for key in self.d:
			self.d[key] = int(self.d[key]) #casts the values to int to be safe
			self.total_weight += self.d[key]

	def pick_key(self):
		"""quick gloss of how this algo works: Create an interval on a number line that stretches from 0 through to self.total_weight (minus 1 cause math reasons). 
			Then pick a random point on this interval and call this your 'target' point. 
			Then for each key in the dictionary, create a smaller interval on the number line with a width equal to that key's weight.
			Then if the random point is contained in one key's interval, that key is returned as the result."""
		
		random_target = random.randint(0, self.total_weight)
		counter = 0
		for key in self.d:
			weight = int(self.d[key])
			if random_target in range(counter, counter + weight): #the smaller intervals I was talking about above are represented as range(counter, counter + weight)
				return key #function call ends if return ever reached
			else:
				counter += weight #moves the starting point of the interval to prepare for next key

class ProbabilityOutOfBoundsError(Exception):
	pass

def read_token():
	with open("token.txt", "r") as f:
		lines = f.readlines()
		return lines[0].strip()
		
def write_dict_into_csv(d, file_name, delimiter=config["csv_delimiter"]): 
	with open(file_name, "w") as f:
		f.write("") #clears the file
	
	with open(file_name, "a") as f:
		for key in d:
			f.write("{}{}{}\n".format(key, delimiter, d[key]))
		
def read_csv_into_dict(file_name, start_row=0, delimiter=config["csv_delimiter"]):
	output_dict = {}
	
	with open(file_name, "r") as f:
		lines = f.readlines() #puts the lines of the csv into the list "lines"
		
		for line_num in range(start_row, len(lines)):
			line_str = lines[line_num]
			line_list = line_str.split(delimiter) #for each line, splits it into a list
			
			new_key = line_list[0].strip() #the 0th and 1st entries in each list are prepared to be the key and value, respectively, in a new key/value pair
			new_value = line_list[1].strip() #the stripping gets rid of whitespace and "\n"s and stuff
			
			output_dict[new_key] = new_value #adds the new key/value pair to the dict
			
	return output_dict

#sets up bot, applies config	
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True) #set up intents
client = commands.Bot(command_prefix=config["command_prefix"], intents=intents) #create bot
client.accuracy = config["default_accuracy"] #sets bot accuracy
client.celebration_probability = config["default_celebration_probability"] #sets bot celebration probability
victory_msgs = WeightDict(read_csv_into_dict(config["victory_message_filename"])) #loads victory messages into proper WeightDict

#============================ Below begins the actual bot stuff
@client.event
async def on_ready():
	print("G'day, mon ami!")
	
@client.event
async def on_member_join(member):
	print("{} has joined the server".format(member))

@client.event
async def on_member_remove(member):
	print("{} has left the server".format(member))

@client.event
async def on_message_delete(message):
	print("A message was deleted.")
	if random.randint(1, 100) <= client.accuracy: #might not be the most elegant way but whatever, I don't care. Yeah, it only properly deals with integer percentage probabilities. It'd be an easy fix probably but idc
		print("Shot hit. Sniping...")
		await message.channel.send("//s")
		if random.randint(1,100) <= client.celebration_probability: #huh apparaently random.randint(a, b) includes b as a possibility
			reply = victory_msgs.pick_key()
			print("Printing victory message.")
			print(reply)
			await message.channel.send(reply)
	else:
		print("Shot missed.")
		
@client.command()
async def ping(ctx):
	await ctx.send("Pong! {}ms".format(round(client.latency * 1000)))

#set bot sniping accuracy
@client.command(aliases=["accuracy", "a"])
async def aim(ctx, new_accuracy="?"):
	#reports the current accuracy if nothing or "?" is input
	if new_accuracy == "?":
		print("Accuracy requested. Accuracy = {}".format(client.accuracy))
		await ctx.send("I hit **{}%** of my shots. \nAlways remember: you miss 100% of the shots you don't take. \nGranted, *you* miss 100% of your shots regardless.".format(client.accuracy))
	
	else:
		#checks if the new value makes sense as an accuracy
		try:
			new_accuracy = int(new_accuracy)
			if not 0 <= new_accuracy <= 100:
				raise ProbabilityOutOfBoundsError
			#sets the accuracy to the new value
			client.accuracy = new_accuracy
			print("Accuracy set to {}%.".format(client.accuracy))
			await ctx.send("Accuracy set to {}%.".format(client.accuracy))
		except ValueError:
			print("Accuracy cannot be set to non-int")
			await ctx.send("My accuracy cannot be set to a non-int, ya bloody simpleton!")
		except ProbabilityOutOfBoundsError:
			print("Accuracy cannot be set outside of [0,100]")
			await ctx.send("My accuracy cannot be set outside of the range [0, 100], ya bloody simpleton!")

#set bot celebration probability
@client.command(aliases=["v"])
async def victory(ctx, new_celebration_probability="?"):
	#reports the current celebration probability if nothing or "?" is input
	if new_celebration_probability == "?":
		print("Celebration probability requested. Probability = {}".format(client.celebration_probability))
		await ctx.send("Victory speech probability: **{}%**".format(client.celebration_probability))
	
	else:
		#checks if the new value makes sense as an celebration probability
		try:
			new_celebration_probability = int(new_celebration_probability)
			if not 0 <= new_celebration_probability <= 100:
				raise ProbabilityOutOfBoundsError
			#sets the celebration probability to the new value
			client.celebration_probability = new_celebration_probability
			print("Victory speech probability set to {}%.".format(client.celebration_probability))
			await ctx.send("Celebration probability set to {}%.".format(client.celebration_probability))
		except ValueError:
			print("Celebration probability cannot be set to non-int")
			await ctx.send("My victory speech probability cannot be set to a non-int, ya bloody simpleton!")
		except ProbabilityOutOfBoundsError:
			print("Celebration probability cannot be set outside of [0,100]")
			await ctx.send("My victory speech probability cannot be set outside of the range [0, 100], ya bloody simpleton!")

token = read_token()
client.run(token)
