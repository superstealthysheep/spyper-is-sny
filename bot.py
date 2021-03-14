import discord
from discord.ext import commands, tasks
import random

command_prefix = "."
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix=command_prefix, intents=intents)

DEFAULT_ACCURACY = 10
client.accuracy = DEFAULT_ACCURACY
DEFAULT_CELEBRATION_PROBABILITY = 25
client.celebration_probability = DEFAULT_CELEBRATION_PROBABILITY

class WeightDict:
	def __init__(self, d): #to be clear, d stands for dictionary
		self.d = d
		self.total_weight = 0

		#self.total_weight is set to be the total of all of the weights in the dict
		for key in d:
			self.total_weight += d[key]

	def pick_key(self):
		"""quick gloss of how this algo works: Create an interval on a number line that stretches from 0 through to self.total_weight (minus 1 cause math reasons). 
			Then pick a random point on this interval and call this your 'target' point. 
			Then for each key in the dictionary, create a smaller interval on the number line with a width equal to that key's weight.
			Then if the random point is contained in one key's interval, that key is returned as the result."""
		
		random_target = random.randint(0, self.total_weight)
		counter = 0
		for key in self.d:
			weight = self.d[key]
			if random_target in range(counter, counter + weight): #the smaller intervals I was talking about above are represented as range(counter, counter + weight)
				return key #function call ends if return ever reached
			else:
				counter += weight

victory_msgs = WeightDict({"All your heads look bloody twelve feet tall.": 10,
				"G'day!": 10,
				"Wave goodbye to your head!": 10,
				"You'd best keep lying down!": 10,
				"Ah, I'm sorry, mate.": 10,
				"That funeral ain't gonna be open casket!": 10,
				"I see ya.": 10,
				"You shouldn't have even gotten outta bed.": 10,
				"This is getting too easy, mate.": 10,
				"How's about ya call it a day?": 10,
				"This is getting embarrassing.": 50,
				"It's only gonna get worse, mate.": 10,
				"I'm just getting warmed up.": 10,
				"That'll slow ya down, ya twitchy hooligan!": 10,
				"Gotcha, ya spastic little gremlin!": 10,
				"Oi, lend us yer shovel, so I can dig yer grave!": 10,
				"Dom-in-ated, ya cactus-eatin' egghead!": 10,
				"Back to the drawin' board, genius!": 10,
				"Not so smart with yer brains outside yer head, are ya?": 10,
				"Nice try, mate, but I'm the best!": 50,
				"You're making this so easy, I'm actually getting worse.": 10,
				"All right!": 10,
				"Piece of piss!": 10,
				"Spot on!": 10,
				"I'm great. You're dead. I think we're done here.": 30,
				"Here's a touchin' story. Once upon a time you died, and I lived happily ever after. The end.": 50,
				"Not so smug now, are ya?": 10,
				"I suspect you'll keep yer big mouth shut now.": 10,
				"Nothing personal, mate.": 10,
				"God Save the Queen!": 50,
				"Now that's downright embarrassing": 10,
				"That's how we do it in the bush!": 40,
				"Sniping's a good job, mate!": 50,
				"All in a day's work.": 10,
				"I told ya sniping was a good job!": 10,
				"I make it look easy": 10,
				"Now that is how it's done!": 10,
				"I could do this all day.": 30,
				"Ahh, that's apples mate.": 10,
				"You got blood on my knife, mate!": 10,
				"A little of the ol' 'chop-chop'!": 10,
				"Bloody hell, you're awful!": 10,
				"That was too easy mate!": 50,
				"No worries.": 10,
				"Cheers, mate.": 10,
				"Bonza.": 10,
				"He he he. Barely broke a sweat!": 10,
				"https://www.youtube.com/watch?v=oyA8EV9QbOQ": 10, #spyper and sny
				"https://www.youtube.com/watch?v=9NZDwZbyDus": 10, #meet the sniper
				"https://www.youtube.com/watch?v=ptW8S-mAbA4": 10, #christian brutal sniper theme
				"https://www.youtube.com/watch?v=jPNkB5Sm7lw": 5, #sniper sees something unsightly
				"https://www.youtube.com/watch?v=5tHUPv7SYdQ": 10 #snia piece of piss
				
				})

class ProbabilityOutOfBoundsError(Exception):
	pass

def read_token():
	with open("token.txt", "r") as f:
		lines = f.readlines()
		return lines[0].strip()

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
	if random.randint(1, 101) <= client.accuracy:
		print("Shot hit. Sniping...")
		await message.channel.send("//s")
		if random.randint(1,101) <= client.celebration_probability:
			reply = victory_msgs.pick_key()
			print("Printing victory message.")
			print(reply)
			await message.channel.send(reply)
	else:
		print("Shot missed.")
		

@client.command()
async def ping(ctx):
	await ctx.send("Pong! {}ms".format(round(client.latency * 1000)))

#This command used to set bot sniping accuracy
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

#This command used to set bot celebration probability
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
			print("Celebration probability set to {}%.".format(client.celebration_probability))
			await ctx.send("Celebration probability set to {}%.".format(client.celebration_probability))
		except ValueError:
			print("Celebration probability cannot be set to non-int")
			await ctx.send("My celebration probability cannot be set to a non-int, ya bloody simpleton!")
		except ProbabilityOutOfBoundsError:
			print("Celebration probability cannot be set outside of [0,100]")
			await ctx.send("My celebration probability cannot be set outside of the range [0, 100], ya bloody simpleton!")

token = read_token()
client.run(token)