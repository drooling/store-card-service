import asyncio
import datetime
import os
import random

import discord
from discord.colour import Color
from selenium import webdriver

block = lambda s: '`' + str(s) + '`'
bold = lambda s: '**' + str(s) + '**'

headless_options = webdriver.FirefoxOptions()
#headless_options.headless = True

async def gen_cards(country: int):
	driver = webdriver.Firefox(executable_path='src\\assets\\geckodriver.exe', service_log_path=os.devnull, options=headless_options)
	driver.get("https://namsogen.co/")
	driver.find_element_by_xpath('//*[@id="ccpN"]').send_keys("60457811436" if country == 0 else "431196")
	driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/section/div[2]/article/div[1]/div/form/div[2]/div[5]/p/input').send_keys('1000')
	driver.find_element_by_xpath('//*[@id="generar"]').click()
	cards = driver.find_element_by_xpath('//*[@id="output2"]').get_attribute('value')
	
	driver.get("https://www.mrchecker.net/card-checker/ccn2/")
	driver.find_element_by_xpath('//*[@id="cc"]').send_keys(cards)
	driver.find_element_by_xpath('/html/body/div/div/div/div/div/div/div[1]/div[2]/form/div[2]/div/button[1]').click()
	await asyncio.sleep(520)
	hits = driver.find_elements_by_xpath('/html/body/div/div/div/div/div/div/div[2]/div[2]/div')
	hits = [hit.text[7:].split('|')[0] for hit in hits]
	driver.close()
	outfile = "src\\assets\\txt\\cards.txt" if country == 0 else "src\\assets\\txt\\uk_cards.txt"
	with open(outfile, 'a') as file:
		file.write('\n'.join(hits) + '\n')
		file.close()
	unique = set(open(outfile).readlines())
	file = open(outfile, 'w')
	file.writelines(set(unique))
	file.close()
	return True

async def gen_aged():
	driver = webdriver.Firefox(executable_path='src\\assets\\geckodriver.exe', service_log_path=os.devnull, options=headless_options)
	for _ in range(50):
		driver.get("https://fakenamegenerator.com/")
		email = str(driver.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/div/div[3]/div[2]/div[2]/div/div[2]/dl[9]/dd').text).split('\n')[0]
		driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")
		driver.find_element_by_xpath('//*[@id="ap_email"]').send_keys(email)
		driver.find_element_by_xpath('//*[@id="continue"]').click()
		try:
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/div[1]/div/div/div/div/ul/li/span')
		except:
			try:
				driver.find_element_by_xpath('//*[@id="continue"]').click()
			except:
				driver.close()
				return email, discord.Embed(title="Amazon Account Generator (__**EARLY**__ BETA)", color=Color.blue(), description="Go to the inbox of {0} and reset the amazon.com password and login.".format(email.lower()))

class AmazonSubscription(object):
    def __init__(self, premium: bool, subscription_end: datetime.date):
        self.premium: bool = premium,
        self.subscription_end: datetime.date = subscription_end

class ConfirmOrder(discord.ui.View):
	def __init__(self, bot: discord.Bot, user: discord.Member, id: str, quantity: int, item: str):
		super().__init__()
		self.bot = bot
		self.user = user
		self.id = id
		self.quantity = quantity
		self.item = item

	@discord.ui.button(label="Payment Received", style=discord.ButtonStyle.green, emoji='\U0001F44D')
	async def ship_product(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.message.reply("Order Confirmed. Product has been delivered.")
		embed = discord.Embed(title="Order Confirmed", description="Your order has been confirmed. Your product will be delivered shortly.", color=Color.green())
		await self.user.send(embed=embed)
		with open("src\\assets\\txt\\cards.txt", 'r') as file:
			cards = list(file.readlines())
			cardz = random.choices(cards, k=self.quantity)
		with open("src\\assets\\txt\\cards.txt", 'w') as file:
			[cards.remove(card) for card in cardz]
			file.writelines(cards)
			file.close()
		embed = discord.Embed(title="Your product(s)", color=Color.green(), description='\n'.join(["${}.00 - {}\n".format(self.item.split(' USD')[0].split('$')[1], card) for card in cardz]))
		embed.set_footer(text="Thank you for purchasing. If you have any problems please contact tragedy#6658.")
		await self.user.send(embed=embed)
		button.disabled = True
		await interaction.message.edit(view=self)

	@discord.ui.button(label="Not Received", style=discord.ButtonStyle.red, emoji='\U0001F44E')
	async def deny_product(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.message.reply("User has been notified.")
		embed = discord.Embed(title="Order Error", description="Your payment has not been received. Please contact tragedy#6658 if you believe this is a mistake.", color=Color.red())
		await self.user.send(embed=embed)
		button.disabled = True
		await interaction.message.edit(view=self)

	@discord.ui.button(label="Refund Issued", style=discord.ButtonStyle.red, emoji='\U0001F9FE')
	async def refund_issued(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.message.reply("User has been notified.")
		embed = discord.Embed(title="Order Error", description="You have been issued a refund. Please contact tragedy#6658 if you believe this is a mistake.", color=Color.red())
		await self.user.send(embed=embed)
		button.disabled = True
		await interaction.message.edit(view=self)

class Confirm(discord.ui.View):
	def __init__(self, bot, id: str, item: str, email: str, quantity: int):
		super().__init__()
		self.confirmed = False
		self.bot = bot
		self.id = id
		self.item = item
		self.email = email
		self.quantity = quantity

	@discord.ui.button(label="Payment Sent", style=discord.ButtonStyle.green, emoji='\U0001F44D')
	async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
		embed = discord.Embed(title="Payment Confirmation ({0})".format(interaction.user), color=Color.blue())
		embed.add_field(name="Item", value=bold(self.item.split(' - ')[0]), inline=False)
		embed.add_field(name="Quantity", value=bold(int(self.quantity)), inline=False)
		embed.add_field(name="Price", value=bold('$' + str((int(self.item.split(' - $')[1]) * self.quantity))), inline=False)
		embed.add_field(name="Paypal Email", value=bold(self.email), inline=False)
		embed.add_field(name="ID", value=bold(self.id), inline=False)
		await interaction.message.reply("Thank you. Your payment is pending human approval.", mention_author=False)
		await self.bot.get_user(875513626805555232).send(embed=embed, view=ConfirmOrder(self.bot, interaction.user, self.id, self.quantity, self.item))
		button.disabled = True
		await interaction.message.edit(view=self)

class ViewInbox(discord.ui.View):
	def __init__(self, email: str):
		super().__init__()
		self.add_item(item=discord.ui.Button(label="View Inbox", style=discord.ButtonStyle.url, url="https://www.fakemailgenerator.com/inbox/{0}/{1}/".format(email.split('@')[1], email.split('@')[0])))