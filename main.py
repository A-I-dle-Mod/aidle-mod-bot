import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents(messages=True, message_content=True, guilds=True, members=True)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print(f'Logged in as {client.user}')

@client.event
async def on_guild_join(guild):
  print(f'Joined guild: {guild.name} (id: {guild.id})')

  r = requests.post(
    os.getenv('API_URL') + '/guild',
    json={
      "owner_id": guild.owner_id,
      "owner_name": guild.owner.name,
      "owner_icon": str(guild.owner.avatar.url) if guild.owner.avatar else None,
      "guild_name": guild.name,
      "guild_id": guild.id,
      "guild_icon": str(guild.icon.url) if guild.icon else None,
      "moderate": True
    }
  )

  print('Guild registration response:', r.json())

@client.event
async def on_guild_remove(guild):
  print("Got remove guild request")

  r = requests.delete(
    os.getenv('API_URL') + '/guild/' + str(guild.id)
  )

  print(f'Removed from guild: {guild.name} (id: {guild.id})')

@client.event
async def on_message(message):
  print(f'Message from {message.author}: {message.content}')

  if message.author == client.user:
    return

  r = requests.post(
    os.getenv('API_URL') + '/moderate',
    json={
      "input_text": message.content,
      'metadata': {
        'message_id': message.id,
        'author_id': message.author.id,
        'author_name': message.author.global_name,
        'guild_id': message.guild.id
      }
    }
  )

  results = r.json()
  
  if results["moderate"] == True:
    await message.delete()
    await message.channel.send('<@' + str(message.author.id) + "> message moderated")

  if message.content.startswith('!hello'):
    await message.channel.send('Hello! How can I assist you today?')

client.run(os.getenv('BOT_TOKEN'))