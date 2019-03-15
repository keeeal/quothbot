import os, random, asyncio, json, discord

def load_messages(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    messages = {}
    users, u_idx = data['meta']['users'], data['meta']['userindex']

    for channel_id, channel_data in data['data'].items():
        for message_id, message_data in channel_data.items():
            u = users[u_idx[message_data['u']]]['name']
            m = message_data['m']

            if not len(m): # empty
                continue
            if 'http' in m or 'www.' in m: # urls
                continue
            if m.startswith('!') or m.startswith('-') or m.startswith(';;'): # bot commands
                continue
            if m.startswith('<@') and m.endswith('>'): # lone tags
                continue

            if u in messages:
                messages[u] += [m]
            else:
                messages[u] = [m]

    users_path = json_path.split('.')
    users_path = '.'.join(users_path[:-1] + ['users'] + users_path[-1:])

    if os.path.isfile(users_path):
        with open(users_path, 'r') as f:
            keep_users = ''.join(f.readlines()).split(',')
    else:
        keep_users = []

        for u, m in sorted(messages.items(), key=lambda x: len(x[1]), reverse=True):
            while True:
                keep = input('Keep ' + u + '? (' + str(len(m)) + ' messages) [y/n] ')

                if keep == 'y':
                    keep_users.append(u)
                    break
                elif keep == 'n':
                    break

        with open(users_path, 'w') as f:
            for user in keep_users:
                f.write(user + ',')

    return {k:v for k, v in messages.items() if k in keep_users}

def get_embed(channel, messages):
    members = channel.server.members
    user = random.choice(list(messages.keys()))
    member = discord.utils.find(lambda m: m.name == user, members)

    if member.nick:
        name = member.nick
    else:
        name = user

    if member.avatar_url:
        avatar_url = member.avatar_url
    else:
        avatar_url = member.default_avatar_url

    message = random.choice(messages[user])
    embed = discord.Embed(description=message)
    embed.set_author(name=name, icon_url=avatar_url)

    return embed

def main(json_file):
    print('\nLoading', json_file, '...')
    messages = load_messages(json_file)
    client = discord.Client()

    @client.event
    async def on_ready():
        print('\nLogged in as', client.user.name, '\n')

        for u, m in sorted(messages.items(), key=lambda x: len(x[1]), reverse=True):
            print(u, '-', len(m), 'messages')

    @client.event
    async def on_reaction_add(reaction, user):
        channel = reaction.message.channel

        if reaction.emoji == '🐦':
            await client.send_message(channel, embed=get_embed(channel, messages))

    with open('token.txt') as f:
        token = f.readline()[:-1]

    while True:
        try:
            client.run(token)
        except KeyboardInterrupt:
            raise
        except:
            pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file')
    main(**vars(parser.parse_args()))
