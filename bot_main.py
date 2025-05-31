from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import commands
import prod_scraper
import os

# Load the .env file
load_dotenv(dotenv_path='bot.env')

# Get the token from environment variable
TOKEN = os.getenv("discord_token")

# Intents are required for newer versions of discord.py
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)




# --------------------| Event Definitions |--------------------

@bot.event
async def on_ready():
    print(f"🤖 Bot is logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "hello":   
        await message.channel.send("Hi there!")  # 👈 must use await

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    print(f"[ERROR]: {type(error).__name__} - {error}")        # error handler for any kind of command error.
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ You forgot to add the required argument!")

    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Such command doesn't exist! Try `!help` to view all the available Commands.")

    else:
        await ctx.send("⚠️ An unexpected error occurred.")




# --------------------| Command Definitions |--------------------


@bot.command(name="help")
async def custom_help(ctx):

    help_text = """
    **Prefix Based Commands:**

    `!help` - Shows this help message.
    `!find <product id/name>` - Find the product's info by its id or name.
    `!find random` - Finds a random product.
    `!cat` - Gives you a list of available categories to choose from using reactions.
    

    **Simple Text Commands:**

    `hello` - Greets the user.
    

    """
    
    custom_embed = discord.Embed(
        description= help_text,      
        color= discord.Colour.green()
        )


    await ctx.send(embed= custom_embed)

@bot.command(name= "find")
async def find(ctx, *, arg):                    # finds a particular product by its ID or Name.
    
    prod_input = arg

    if prod_input.lower() == "random":          # finds a random product.
        await ctx.send("Finding a random product for you..")
        prod_data = prod_scraper.get_random_prod()          
    else:                                       # finds by id or name.
        await ctx.send("Finding the product for you...")
        prod_data = prod_scraper.get_prod_data(prod_input)

    if "error_message" in prod_data:

        custom_embed = discord.Embed(
            title= "Error!",
            description= f'> {prod_data["error_message"]}',
            color= discord.Colour.red(),
            )
        
        await ctx.send(embed=custom_embed)

    else:
        p_name = prod_data["title"]
        p_desc = prod_data["description"]
        p_price = prod_data["price"]
        p_category = prod_data["category"]["name"]
        p_id = prod_data["id"]

        p_thumbnail = prod_data["images"][0]
        p_image = prod_data["images"][1] if len(prod_data["images"]) > 1 else prod_data["images"][0]

        custom_embed = discord.Embed(
            title= p_name,
            description= f"> *{p_desc[:128]}...*",      #limited to 128 characters
            color= discord.Colour.green(),
            )

        custom_embed.set_thumbnail(url= p_thumbnail)
        custom_embed.set_image(url= p_image)

        custom_embed.add_field(name= "ID:", value= p_id, inline=True)
        custom_embed.add_field(name= "Category", value= p_category, inline=True)
        custom_embed.add_field(name= "Price", value= f"`${p_price}`", inline=False)

        await ctx.send(embed=custom_embed)

@bot.command(name= "cat")
async def category(ctx):                        # gives an interactvie list of available categories and products in them.

    cat_data = prod_scraper.get_cat_data() 

    cat_list_text = ''

    for index, element in enumerate(cat_data, 1):
        cat_list_text += f"> `{index}. {element}`\n"


    main_embed = discord.Embed(
            title= "List of Categories",
            description= f"Select any of the available categories to view the products listed under them.\n{cat_list_text}", 
            color= discord.Colour.green(),
            )

    message = await ctx.send(embed=main_embed)
    

    number_emojis = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
    }

    for index, element in enumerate(cat_data, 1):
        await message.add_reaction(f'{number_emojis[index]}')

    def check(reaction, user):          # returns a single True or False boolean.
        return (user == ctx.author and 
                reaction.message.id == message.id
                )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout= 8.0, check=check)

    except asyncio.TimeoutError:
        await ctx.send(f"You took too long to respond!")
    else:
        for x in number_emojis:
            if number_emojis[x] == str(reaction):
                selected_option = str(x)

        await ctx.send(f"You selected option: {selected_option}")

        prods_in_cat = prod_scraper.get_prods_by_cat(selected_option)

        sub_embed = discord.Embed(
            title= "List of Products in Category",
            description= "*For more info about the product use this command:* `!find <id here>`",
            color= discord.Colour.green(),
            )
        
        for x in prods_in_cat:
            sub_embed.add_field(name= f"Product ID: `{x['id']}`", value= f"{x['title']}" , inline=False)

        await ctx.send(embed=sub_embed)



# Replace with your bot token
bot.run(TOKEN)