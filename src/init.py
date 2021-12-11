import asyncio
import logging
import os
import random
import sys
import traceback
import uuid

import discord
from discord.colour import Color
from discord.commands import Option, context
from dotenv import load_dotenv

from ext import Confirm, ViewInbox, gen_aged, gen_cards
from mysql import convert_to_bool, convert_to_emoji, Amazon_DB

load_dotenv('.env')

bot = discord.Bot("/", intents=discord.Intents.all(), case_insensitive=True, strip_after_prefix=True, loop=asyncio.get_event_loop(), owner_id=875513626805555232)

Database = Amazon_DB()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bold = lambda s: '**' + str(s) + '**'
block = lambda s: '```' + str(s) + '```'


@bot.event
async def on_application_command_error(interaction: context.ApplicationContext, error: Exception):
	await interaction.channel.send("error occured. traceback reported.", delete_after=3)
	exception = block(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
	dev = await bot.fetch_user(875513626805555232)
	await dev.send(exception)

@bot.slash_command(description="Use this command to purchase amazon store cards.")
async def purchase(ctx: context.ApplicationContext, amount: Option(str, "What amount would you like on your store card(s)?", choices=["$200 USD AMAZON CARD - $10", "$1000 USD AMAZON CARD - $35", "$2000 USD AMAZON CARD - $50", "$5000 USD AMAZON CARD -$80", "$10,000 USD AMAZON CARD - $150", "$20,000 USD AMAZON CARD - $170", "$30,000 USD AMAZON CARD - $200"], required=True), email: Option(str, "What is your paypal email?", required=True), quantity: Option(int, "How many cards would you like to purchase?", choices=[1, 2, 3, 4, 5], required=False, default=1)):
	await ctx.respond(embed=discord.Embed(title="Refer to the private message just sent to you !", color=discord.Color.blue()), ephemeral=True)
	id = uuid.uuid4()
	item = amount
	embed = discord.Embed(title="Payment Confirmation", color=Color.blue(), description="To pay, please click the following link [https://paypal.com](https://www.paypal.com/donate/?business=4G3W59KUSTV8W&item_name=Authorized%20Payment%20To%20Surtains&currency_code=USD) and send the specified amount. After you have sent the specified amount click the \"Payment Sent\" button and upon human approval you will receive your product(s). ")
	embed.add_field(name="Item", value=bold(item.split(' - ')[0]), inline=False)
	embed.add_field(name="Quantity", value=bold(int(quantity)), inline=False)
	embed.add_field(name="Price", value=bold('$' + str((int(item.split(' - $')[1]) * quantity))), inline=False)
	embed.add_field(name="Paypal Email", value=bold(email), inline=False)
	embed.add_field(name="ID", value=bold(id), inline=False)
	embed.set_footer(text="If you have any problems please contact tragedy#6658.")
	await ctx.author.send(embed=embed, view=Confirm(bot, id, amount, email, quantity))

@bot.slash_command(description="Generate store card(s) [Must have plan]")
async def generate(ctx: context.ApplicationContext, country: Option(str, "What country would you like the cards too be from?", choices=["USA", "UK"]), amount: Option(int, "Select the amount you would like on your store card(s)", choices=[200, 500, 700, 1000, 2000, 5000, 10000, 20000, 30000, 40000, 50000], required=True), quantity: Option(int, "How many store cards would you like?", choices=[1, 2, 3, 4, 5], required=False, default=1)):
	await Database.confirm_buyer(ctx, ctx.author)
	if country == "USA":
		infile = "src\\assets\\txt\\cards.txt"
		currency = "$"
	elif country == "UK":
		infile = "src\\assets\\txt\\uk_cards.txt"
		currency = "£"
	with open(infile, 'r') as file:
		cards = list(file.readlines())
		cardz = random.choices(cards, k=quantity)
	with open(infile, 'w') as file:
		[cards.remove(card) for card in cardz]
		file.writelines(cards)
		file.close()
	await ctx.respond(embed=discord.Embed(title="Amazon Store Card Generator ({0})".format(country), color=Color.blue(), description='\n'.join(["{0}{1}.00 - {2}".format(currency, amount, card) for card in cardz]) + "\n**Rules of use** - [Click here](https://pad.riseup.net/p/r.9d92f9efea6c904f087e9ffa9a9353c4)"), ephemeral=True)

@bot.slash_command(description="Restock card supply")
async def restock(ctx: context.ApplicationContext, country: Option(str, "What country?", choices=["UK", "USA"], required=True)):
	await ctx.defer()
	await gen_cards((0 if country == "USA" else 1))
	await ctx.respond("Finished Re-stocking cards.", ephemeral=True)

@bot.slash_command(description="Generates a aged amazon account")
async def aged(ctx: context.ApplicationContext):
	await Database.confirm_buyer(ctx, ctx.author)
	await ctx.defer()
	email, embed = await gen_aged()
	await ctx.respond(embed=embed, view=ViewInbox(email), ephemeral=False)

@bot.slash_command(description="View user's plan.")
async def plan(ctx: context.ApplicationContext, member: Option(discord.Member, "Choose the member to view the plan details of", required=True)):
	plan = Database.get_user(member=member)
	if not plan:
		return await ctx.respond(embed=discord.Embed(color=Color.blue(), description="User Has No Active Plan. To purchase one message tragedy#6658."))
	await ctx.respond(embed=discord.Embed(title=member, color=Color.blue(), description="Premium Plan - {0}\nPlan Expiration - **{1}**".format(convert_to_emoji(convert_to_bool(plan.premium)), plan.subscription_end)))

bot.run(os.getenv("token"))