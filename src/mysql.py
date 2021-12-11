import asyncio
import collections
import datetime
import functools
import logging
import os
import sys
import threading
import typing

import discord
import pymysql.cursors
from discord.commands import context
from dotenv import load_dotenv

from ext import AmazonSubscription

load_dotenv('.env')

convert_to_bool = lambda i: False if i == 0 else True
convert_to_emoji = lambda i: "\U00002705" if i == True else "\U0001F1FD"


class Amazon_DB:
	def __init__(self) -> None:
		self.pool = pymysql.connect(host=os.getenv("mysqlServer"), user="root", password=os.getenv("mysqlPassword"), port=3306, database="tragedy", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, read_timeout=5, write_timeout=5, connect_timeout=5, autocommit=True)
		
		self.logger = logging.getLogger('amazon.db')
		self.logger.setLevel(logging.INFO)
		handler = logging.StreamHandler(stream=sys.stdout)
		handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
		self.logger.addHandler(handler)

		self.ensure_mysql()

	def ensure_mysql(self):
		if not self.pool.open:
			self.pool.ping(reconnect=True)
		self.logger.log(logging.INFO, "ENSURED MySQL connection ACTIVE.")
		threading.Timer(35, self.ensure_mysql).start()

	def plan_expiration(self):
		deleted = collections.deque([], maxlen=3)
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT user, plan_expiration FROM `amazon`")
			records = cursor.fetchall()
		for record in records:
			if record.get("plan_expiration") <= datetime.datetime.now().date():
				cursor.execute("DELETE FROM `amazon` WHERE user=%s", (record.get("user")))
				deleted.append(record.get("user"))
		self.logger.log(logging.INFO, "DELETED {0} from AMAZON table.".format((', '.join(deleted) + '...') if deleted else "NONE"))

	@functools.lru_cache(maxsize=None)
	def amazon_buyers(self) -> typing.Union[typing.List[int], typing.Set[int]]:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT user FROM `amazon`")
			rows = cursor.fetchall()
		buyers = [entry.get("user") for entry in rows]
		return set(buyers) or []

	async def confirm_buyer(self, ctx: context.ApplicationContext, customer: typing.Union[discord.Member, discord.User]) -> None:
		if customer.id not in self.amazon_buyers():
			return await ctx.respond("Hey ! You do not have access to this command. To purchase a plan please contact tragedy#6658 !", ephemeral=True)
		else:
			pass

	def get_user(self, member: discord.Member) -> AmazonSubscription:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT premium, plan_expiration FROM `amazon` WHERE user=%s", (member.id))
			row = cursor.fetchone()
		try:
			return AmazonSubscription(convert_to_bool(int(row.get("premium"))), row.get("plan_expiration"))
		except AttributeError:
			return False