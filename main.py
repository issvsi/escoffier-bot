import discord
import random
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv() # all env stuff is here do not remove this line or else you are FUCKED (bot safety reasons)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event # when bot is on
async def on_ready():
    print("Bot is ready")
    log = client.get_channel(1382448506488488016)
    await log.send("Bot is online! :white_check_mark:")
    
    global issvsi
    global msglog
    global consolelog
    global prefix
    global blacklist
    global blacklist_file

    blacklist_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blacklist.json")
    issvsi = int(os.getenv('issvsi_id'))
    msglog = client.get_channel(int(os.getenv('msglog_id')))
    consolelog = client.get_channel(int(os.getenv('console_id')))
    prefix = os.getenv('prefix')

    with open(blacklist_file, "r") as file:
        blacklist = json.load(file)

@client.event # when somebody invites le bot
async def on_guild_join(guild):
    owner = await guild.fetch.owner()
    print(f"Joined a server. \n Name: {guild.name} \n ID: {guild.id} \n Owner ID: {guild.owner.id} \n Owner username: {guild.owner.global_name}")
    log = client.get_channel(1382448506488488016)
    await log.send(f"Joined a server. \n Name: {guild.name} \n ID: {guild.id} \n Owner ID: {owner.id} \n Owner username: {owner.global_name}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.id in blacklist:
        return
    
    # DM bridge (log the DM)

    if isinstance (message.channel, discord.DMChannel):
        user = message.author
        user_name_check = user.global_name or user.name
        unix = int(user.created_at.timestamp())
        embed = discord.Embed(
            title = f"**__Message: __**",
            description = message.content,
            color = discord.Color.green()
        )
        embed.add_field(
            name = "**__User ID: __**",
            value = user.id,
            inline = True
        )
        embed.add_field(
            name = "**__Username: __**",
            value = user.global_name,
            inline = True
        )
        embed.add_field(
            name = "**__Nickname: __**",
            value = user.name,
            inline = True
        )
        embed.add_field(
            name = "**__Joined: __**",
            value = f"<t:{unix}:F>",
            inline = True
        )
        embed.set_thumbnail(url=user.avatar.url)
        if msglog:
            await msglog.send(embed = embed, content = f"New message from {user_name_check}")
        else:
            return
        
    # super duper advanced reply system (exclusive to me uwu)

    if message.channel == msglog:
        if message.author.id == issvsi:
            if message.content.startswith("!reply"):
                cmd_parts = message.content.split(" ", 2)
                if len(cmd_parts) < 3:
                    await message.channel.send("Something went wrong. Correct usage (in case you fucking forgot: \n `reply_to userid message_here)")
                    return
                
                _, userid_string, message_to_send = cmd_parts
                try:
                    userid = int(userid_string)
                    user = await client.fetch_user(userid)
                    await user.send(message_to_send)
                    await message.channel.send(f":white_check_mark: Sent message to {user.name}")
                except Exception as error:
                    await message.channel.send(":x: There was an issue with sending message to that user. Try again.")

        else:
            await message.channel.send("Only bot owner can use this feature.")
        
    # commands (with prefix)

    if message.content.startswith(prefix):
        parts = message.content[len(prefix):].split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "help": # !help
            await message.channel.send("For list of commands, please use `!commands`. \n -# Bot made by issvsi \n **THIS IS A PRIVATE BOT, EXPECT ERRORS. For any questions, DM me (through bot DMs)")
        
        if command == "commands":
            if message.author.id == issvsi:
                embed= discord.Embed(
                    title = "Admin Commands",
                    description = "`help` \n `commands` \n `8ball` \n `dice` \n `kaput` :shield:"
                )
                await message.channel.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = "**Command List**",
                    description = "`help` \n `commands` \n `8ball` \n `dice`"
                )
                await message.channel.send(embed = embed)

        if command == "8ball":
            replies = [
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes." ,
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again."
            ]
            reply = random.choice(replies)
            await message.channel.send(reply)
        
        if command == "dice":
            if args:
                if args[0].isdigit():
                    max_roll = int(args[0])
                    if max_roll > 1:
                        roll = random.randint(1, max_roll)
                        await message.channel.send(f"Your roll is {roll}")
                    else:
                        await message.channel.send("Error. Please make sure your number IS a number, is not negative and is higher than 1.")
                else:
                    await message.channel.send("Please pick a number.")
            else:
                await message.channel.send("Please provide an input (Number, must be greater than 1.)")
        
        if command == "blacklist":
            if message.author.id == issvsi:
                if args:
                    if args[0] == "remove":
                        if args[1].isdigit():
                            user_id = int(args[1])
                            user = await client.fetch_user(user_id)
                            username = user.name
                            if user_id in blacklist:
                                blacklist.remove(user_id)
                                with open(blacklist_file, "w") as f:
                                    json.dump(blacklist, f)
                                await message.channel.send(f"Removed {username} from the blacklist.")
                                await consolelog.send(f"Removed {username} from the blacklist.")
                            elif user_id not in blacklist:
                                await message.channel.send(f"{username} is not in the blacklist.")
                        else:
                            await message.channel.send("Provide correct user ID.")
                    elif args[0] == "list":
                        if len(blacklist) > 1:
                            embed = discord.Embed(
                                title = "List of blacklister users:",
                                description = blacklist
                            )
                            await message.channel.send(embed = embed)
                        else:
                            embed = discord.Embed(
                                title = "List of blacklister users:",
                                description = "Blacklist is empty!"
                            )
                            await message.channel.send(embed = embed)
                    elif args[0].isdigit():
                        user_id = int(args[0])
                        user = await client.fetch_user(user_id)
                        username = user.name
                        if user_id not in blacklist:
                            blacklist.append(user_id)
                            with open(blacklist_file, "w") as f:
                                json.dump(blacklist, f)
                            await message.channel.send(f"Successfully blacklisted {username}")
                            await consolelog.send(f"Successfully blacklisted {username}")
                        else:
                            await message.channel.send("User is already blacklisted.")
                    else:   
                        await message.channel.send("Please provide correct user ID.")
                else:
                    await message.channel.send("Please provide correct user ID.")
            else:
                await message.channel.send("Only bot owner can run this command..")
            
        
        # suicide
        if command == "kaput":
            if message.author.id == issvsi:
                print("Bot fucking died (suicide)")
                await consolelog.send("Bot fucking died (suicide)")
                await client.close()
            else:
                await message.channel.send("Only bot owner can run this command..")

    # secrets uwu

    if "crazy" in message.content.lower().replace(" ", ""):
            for x in range(5):
                await message.channel.send("Crazy? I was crazy once. They locked me in a room. A rubber room. A rubber room with rats. And rats make me crazy.")
                await asyncio.sleep(3)

    if "touhou" in message.content.lower().replace(" ", ""):
        await message.channel.send("toe hoe")

    if "toehoe" in message.content.lower().replace(" ", ""):
        await message.channel.send("fuck you that's my line from now on")

    if "sus" in message.content.lower().replace(" ", ""):
        await message.channel.send("ඞ")

    if "stfu" in message.content.lower().replace(" ", ""):
        await message.channel.send("https://media.discordapp.net/attachments/1374712762395131955/1393400675353890896/ezgif.com-video-to-gif-converter.gif?ex=68730901&is=6871b781&hm=d15af3db78dcb76a738efa58294d03f887eadeefc2da2cc5c453e7c6ccd9eaba&=")
    
    if "papa" in message.content.lower().replace(" ", ""):
        await message.channel.send("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHYwanV2eTllb3VoMW1zY3drNHFsOHdjcWU1YWc4bHk4enFnYzViOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GR67sEladxNpWE667V/giphy.gif")

    if len(message.content) > 500:
        await message.channel.send("Holy yap")
    
    if isinstance(message.channel, discord.TextChannel):
        chance = 0.01
        if random.random() < chance:
            replies = [
                "https://media.discordapp.net/attachments/1233638887532920875/1297368325839654943/togif.gif?ex=687260a8&is=68710f28&hm=76b4c0ae1b2288a1966a2b053ce4b2663e560a7aec204a6f3883dfc7b89262e8&=",
                "https://media.discordapp.net/attachments/1164423777086619678/1198853674542309376/speechmemified_pasteimage.gif?ex=687293bd&is=6871423d&hm=5361ebbc868d356d2c62f7a8159b323d4695fb60e733f83c1d9e98ca4d147d0e&=",
                "https://media.discordapp.net/attachments/1386823437053464646/1388290471817641984/togif.gif?ex=6872e6c1&is=68719541&hm=3e871871a786644c2f56d8aab0d0b84d23ef64c57ddc23002d6d9cd9a5eacf24&=",
                "https://media.discordapp.net/attachments/1131496897757057067/1255475258551570462/attachment.gif?ex=6872e6b3&is=68719533&hm=cfc28c676f2baebe878c9d7f2cb7b0f9ba0690cefcb7430a50a458e5c6a77daf&=",
                "https://media.discordapp.net/attachments/1284359795440357417/1285228705433784351/caption.gif?ex=68726101&is=68710f81&hm=a32ad483d73c876e53bc9390ccbca5880bd9986656d8896ff3efbc3a1dc0313e&=",
                "https://media.discordapp.net/attachments/1356765177298817105/1371860229158993980/caption-20.gif?ex=68727466&is=687122e6&hm=09cbef9e7e240bc9029cc6e382856c67c3f85610e28ce213b41c795efde69af5&=",
                "https://media.discordapp.net/attachments/808775962656899105/952287620317212724/08978764.gif?ex=684e76b5&is=684d2535&hm=f2bcc75ffa4c148f55511701b8a29a2151b0dc42785287a3242696f8c8488345&=",
                "https://media.discordapp.net/attachments/697469930240606258/1069807327512903690/urDRAFTEDteehee.gif?ex=684e30b6&is=684cdf36&hm=ab5207386af0d85628c2325888b2395d821e1900d7e527da3d43b88f9fec143a&=",
                "https://media.discordapp.net/attachments/1239343801391120398/1268134667597381673/togif-5.gif?ex=684e8ef1&is=684d3d71&hm=39107c7f2b1fdd52d5bd12d0a4673004e217ca08cb7ae38c52ed95d7b4520e54&=&width=979&height=960",
                "https://media.discordapp.net/attachments/935989994735169546/1049368698693111948/attachment.gif?ex=684e5282&is=684d0102&hm=ad760df2f0851bc3bca35fa6c05b2236419caf9fc3b6f9974f27d6752754be3b&=",
                "https://media.discordapp.net/attachments/949479291635261450/1133285499268767844/attachment-3.gif?ex=684e68de&is=684d175e&hm=c3e7ae5392e50af85887c37c4ac7fc2baa36c398f30acd1c1236111f8c2d1a7f&=",
                "https://media.discordapp.net/attachments/987789131801313304/1170818615860281424/togif-1.gif?ex=684e810e&is=684d2f8e&hm=508f68de7e56dfbc3fb2afc5410a2bf0262c9d380dbcd3d54993ea850f86639c&="
            ]
            reply = random.choice(list(replies))
            await message.channel.send(reply)
    
    if "judgement" in message.content.lower().replace(" ", ""):
        await message.channel.send("https://tenor.com/view/minos-prime-ultra-kill-ultrakill-prowler-meme-prowler-gif-3786873416559560912")
    
    if "loss" in message.content.lower():
        await message.channel.send("⠀⠀⠀⣴⣴⡤\n⠀⣠⠀⢿⠇⡇⠀⠀⠀⠀⠀⠀⠀⢰⢷⡗\n⠀⢶⢽⠿⣗⠀⠀⠀⠀⠀⠀⠀⠀⣼⡧⠂⠀⠀⣼⣷⡆\n⠀⠀⣾⢶⠐⣱⠀⠀⠀⠀⠀⣤⣜⣻⣧⣲⣦⠤⣧⣿⠶\n⠀⢀⣿⣿⣇⠀⠀⠀⠀⠀⠀⠛⠿⣿⣿⣷⣤⣄⡹⣿⣷\n⠀⢸⣿⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿\n⠀⠿⠃⠈⠿⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠿⠿⠿\n \n⠀⢀⢀⡀⠀⢀⣤⠀⠀⠀⠀⠀⠀⠀⡀⡀\n⠀⣿⡟⡇⠀⠭⡋⠅⠀⠀⠀⠀⠀⢰⣟⢿\n⠀⣹⡌⠀⠀⣨⣾⣷⣄⠀⠀⠀⠀⢈⠔⠌\n⠰⣷⣿⡀⢐⢿⣿⣿⢻⠀⠀⠀⢠⣿⡿⡤⣴⠄⢀⣀⡀\n⠘⣿⣿⠂⠈⢸⣿⣿⣸⠀⠀⠀⢘⣿⣿⣀⡠⣠⣺⣿⣷\n⠀⣿⣿⡆⠀⢸⣿⣿⣾⡇⠀⣿⣿⣿⣿⣿⣗⣻⡻⠿⠁\n⠀⣿⣿⡇⠀⢸⣿⣿⡇⠀⠀⠉⠉⠉⠉⠉⠉⠁\n⠀⠛⠛⠃⠀⠘⠛⠛⠃")

TOKEN = os.getenv('TOKEN')
client.run(TOKEN)