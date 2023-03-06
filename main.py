from discord.ui import View, Button
import discord
import sqlite3
from discord.ext import commands

token = ''
intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix="?!", intents=intents)

category_names = ['Other', 'Game-related Issue', 'Ban-related', 'Discord-related', 'Reports']

db = sqlite3.connect('modmail.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS modmail (
        user_id int,
        channel_id int
     )
""")


class CategoryView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        for category in category_names:
            self.add_item(Button(label=category, custom_id=category))


    async def interaction_check(self, interaction: discord.Interaction):
        # Only allow interactions from the user who started the ticket
        cursor.execute("SELECT user_id FROM modmail WHERE user_id = (?)", (interaction.user.id,))
        if cursor.fetchone() is not None:
            #if the user exists
            return False
        guild = client.get_guild(940455965625573386)
        
        category = str(interaction.data['custom_id'])
        
        
        category_disc = discord.utils.get(guild.categories, name=category)
        
        channel = await category_disc.create_text_channel(f"{interaction.user.name}-{str(interaction.user.id)}")
        channel_id = channel.id
        
        cursor.execute("INSERT INTO modmail VALUES (?, ?)", (
                        interaction.user.id,
                        channel_id,
                    ))
        
        db.commit()
        
        await interaction.response.send_message(f"```Your ticket ({category}) has been created! Please ask your question and wait for a staff member to respond.```")
        
        user = interaction.user
        embed = discord.Embed(title=f"{user.name}'s Information", color=0x00ff00)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="Discriminator", value=user.discriminator, inline=False)
        embed.add_field(name="User ID", value=user.id, inline=False)
        await channel.send(embed=embed)
        
        return interaction.user.id == self.user_id
    

class AgmaSupportEmbed(discord.Embed):
    def __init__(self, description, **kwargs):
        super().__init__(**kwargs)
        self.title = "Agma.io Support Bot"
        self.description = description
        self.color = 0xFF5733
        self.set_author(name="Agma.io Staff Team")
        self.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/942143239631302656/942669002084352051/Agma.png"
            )



@client.event
async def on_message(ctx):
    
    await client.process_commands(ctx)
    
    # Check if the message is a direct message
    if isinstance(ctx.channel, discord.DMChannel):
        if ctx.author == client.user:
            return
        if not ctx.guild:
            cursor.execute("SELECT user_id FROM modmail WHERE user_id = (?)", (ctx.author.id,))
            if cursor.fetchone():
                # User exists, fetch the existing channel id
                cursor.execute("SELECT channel_id FROM modmail WHERE user_id = (?)", (ctx.author.id,))
                channel_id = cursor.fetchone()[0]
                channel = client.get_channel(channel_id)
                await channel.send(f"***{ctx.author.name}*** - {ctx.content}")
            else:
                guild = client.get_guild(940455965625573386)
                category_view = CategoryView(user_id=ctx.author.id)
                dm_channel = await ctx.author.create_dm()
                
                
                
                await dm_channel.send(embed=AgmaSupportEmbed("Please select a category for your support thread"), view=category_view)
                
    else:
        return
    
    

    

@client.command(name="close")
@commands.has_any_role('Agma.io Owner', "Agma.io Staff", "Agma.io Support",
                       "Agma.io Moderator", "Bot Creator")
async def closed(ctx):
    try:
        channel_cls = ctx.channel
        channel_name = ctx.channel.name.split('-')
        user = client.get_user(int(channel_name[-1]))

        embed = discord.Embed(
            title="Agma.io Support Bot",
            description=
            "Your thread has been closed by a staff member, Messaging this bot again will start another support thread.",
            color=0xFF5733)

        embed.set_author(name="Agma.io Staff Team")

        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669002084352051/Agma.png"
        )

        await user.send(embed=embed)

        await channel_cls.delete()
        log_channel = client.get_channel(942762723199045692)
        await log_channel.send(f"{ctx.author} has closed the channel {ctx.channel}"
                            )
        cursor.execute("DELETE FROM modmail WHERE channel_id = (?)",
                    (channel_cls.id, ))
        db.commit()
        print("Channel closed")
    except Exception as e:
        await ctx.channel.send(e)
        await ctx.channel.send("Error code FORBIDDEN")
        
@client.command(name="m")
async def messagea(ctx, *, text):
    channel_name = ctx.channel.name.split('-')
    user = client.get_user(int(channel_name[-1]))
    """MESSAGE COMMAND"""
    if "agma.io staff" in [y.name.lower() for y in ctx.author.roles]:
        happy_channel = client.get_channel(943825031920775179)

        embed = discord.Embed(title="Agma.io Support Bot",
                              description=text,
                              color=0xFF5733)

        embed.set_author(
            name="Agma.io Staff",
            icon_url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669001509699584/Staff_Crown.png"
        )

        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669002084352051/Agma.png"
        )
        ##########################

        await ctx.channel.purge(limit=1)
        await user.send(embed=embed)
        await ctx.channel.send(f"**Agma.io Staff({ctx.author.name})**: {text}")
        await happy_channel.send(f"**{ctx.author}(STAFF)**: {ctx.content}")
        print("STAFF sent a message")

    elif "agma.io moderator" in [y.name.lower() for y in ctx.author.roles]:
        happy_channel = client.get_channel(943825031920775179)

        embed = discord.Embed(title="Agma.io Support Bot",
                              description=text,
                              color=0xFF5733)

        embed.set_author(
            name="Agma.io Moderator",
            icon_url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669001258057769/AgmaMods.png"
        )

        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669002084352051/Agma.png"
        )
        ##########################

        await ctx.channel.purge(limit=1)
        await user.send(embed=embed)
        await ctx.channel.send(
            f"**Agma.io Moderator({ctx.author.name})**: {text}")

    elif "agma.io support" in [y.name.lower() for y in ctx.author.roles]:
        happy_channel = client.get_channel(943825031920775179)

        embed = discord.Embed(title="Agma.io Support Bot",
                              description=text,
                              color=0xFF5733)

        embed.set_author(
            name="Agma.io Support",
            icon_url=
            "https://cdn.discordapp.com/attachments/942665547357777940/942665740140560434/imageonline-co-transparentimage_35.png"
        )

        embed.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/942143239631302656/942669002084352051/Agma.png"
        )
        ##########################

        await ctx.channel.purge(limit=1)
        await user.send(embed=embed)
        await ctx.channel.send(
            f"**Agma.io Support({ctx.author.name})**: {text}")
        print("Message sent")

    elif "agma.io owner" in [y.name.lower() for y in ctx.author.roles]:
        happy_channel = client.get_channel(943825031920775179)

        embed = discord.Embed(title="Agma.io Support Bot",
                              description=text,
                              color=0xFF5733)

        embed.set_author(
            name="Agma.io Admin",
            icon_url=
            "https://cdn.discordapp.com/attachments/942665547357777940/942672927034331167/701119381559574558.webp"
        )

        await ctx.channel.purge(limit=1)
        await user.send(embed=embed)
        await ctx.channel.send(f"**Agma.io Admin({ctx.author.name})**: {text}")
        await happy_channel.send(f"**{ctx.author}(ADMIN)**: {ctx.content}")
        print("OWNER sent a message")

    else:
        await ctx.channel.send(
            "ERROR: YOU DO NOT HAVE PERMISSIONS TO PERFORM THIS ACTION. (PermissionError (If you are a registered support user please message 'Happy?#5111')) ❌"
        )
        print("Message error (PermissionError) user - " + str(ctx.author))


@client.command()
@commands.has_any_role('Agma.io Owner', "Agma.io Staff", "Agma.io Support",
                       "Agma.io Moderator", "Bot Creator")
async def ping(ctx):
    await ctx.channel.send("Pong!")
    

client.run(token)

