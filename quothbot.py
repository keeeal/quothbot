
import os, asyncio, json, pickle
from datetime import datetime
from random import choice

import discord
data = {}

# print, but with a timestamp
def print_log(*args, **kwargs):
    print('[{}]'.format(datetime.now()), *args, **kwargs)

# return a dictionary of guild > messages
async def get_data(client):
    print_log('Getting data')
    data = {}

    for guild in client.guilds:
        print_log(guild.name)
        data[guild] = []

        for channel in guild.text_channels:
            print_log(guild.name, '>', channel.name)
            messages = await channel.history(limit=None).flatten()
            print_log(guild.name, '>', channel.name, '>',
                '{} messages found.'.format(len(messages)))
            data[guild] += messages

    print_log('Ready to quoth')
    return data

def main(config_file):

    # load config file or create it
    if os.path.isfile(config_file):
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {'token': ''}
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    # check for auth token
    if not config['token']:
        print('Error: Token not found.')
        print('Copy bot token into "{}"'.format(config_file))
        return

    # create client
    client = discord.Client()

    @client.event
    async def on_ready():
        global data
        print_log('Logged in as', client.user.name)

        # get data
        data = await get_data(client)

    @client.event
    async def on_reaction_add(reaction, user):
        channel = reaction.message.channel
        if reaction.emoji == '🐦':

            # report no data
            if not data:
                msg = "I can't quoth right now, I'm reading messages."
                embed = discord.Embed(description=msg)
                await channel.send(embed=embed)
                return

            # choose a random message
            message = choice(data[channel.guild])

            # get author name and avatar
            name = message.author.name
            icon_url = message.author.default_avatar_url
            if isinstance(message.author, discord.Member):
                icon_url = message.author.avatar_url
                if message.author.nick:
                    name = message.author.nick

            # embed with author and timestamp
            embed = discord.Embed(
                description=message.content, timestamp=message.created_at)
            embed.set_author(name=name, icon_url=icon_url)

            # if attachments, choose a random one
            if message.attachments:
                embed.set_image(url=choice(message.attachments).url)

            # send to reaction channel
            await channel.send(embed=embed)

    # start bot
    client.run(config['token'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', '-c', default='config.json')
    main(**vars(parser.parse_args()))
