from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
import requests
import datetime
import utils
import json
import time
import sys
import os

url='https://www.bitstamp.net/api/v2/ticker/btcusd/'

load_dotenv()
WEBHOOK = os.getenv('WEBHOOK') 		# CREATE .ENV FILE AND ADD LINE WITH LINK TO YOUR WEBHOOK
CRYPTO_ROLE = os.getenv('CRYPTO') 	# Discord RoleID for members of server to be pinged by bot 

yr = 2021
months = {b'Jan':1,b'Feb':2,
		  b'Mar':3,b'Apr':4,
		  b'May':5,b'Jun':6,
		  b'Jul':7,b'Aug':8,
		  b'Sep':9,b'Oct':10,
		  b'Nov':11,b'Dec':12}

def currentDatetime():
	 ld,lt = utils.create_timestamp()
	 mon = int(ld.split('/')[0])
	 day = int(ld.split('/')[1])
	 yr = int(ld.split('/')[2])
	 hr = int(lt.split(':')[0])
	 mn = int(lt.split(':')[1])
	 sec = int(lt.split(':')[2])
	 return datetime.datetime(yr,mon,day,hr,mn,sec)


class DiscordMsg:
	def __init__(self, msgType, msgData):
		self.mode = msgType
		self.data = msgData
		# Depending on mode may send different type of message 

	def send_message(self):
		# Send a message
		webhook = DiscordWebhook(
								url=WEBHOOK, 
								rate_limit_retry=True,
								content=self.data['content'])
		response = webhook.execute()

class CryptoBot:
	def __init__(self):
		self.startld, self.startlt = utils.create_timestamp()
		initial = self.get_current_price_data()
		self.price = float(initial['last'])
		self.running = True
		print(f'Initial Price: ${self.price}')
		msg = f'<@&{CRYPTO_ROLE}> *Current BTC Price* is **${self.price}**'
		DiscordMsg('text',{'content':msg}).send_message()

	def get_current_price_data(self):
		raw = requests.get(url).text
		return json.loads(raw)



	def run(self):
		while self.running:
			try:
				time.sleep(60)
				latest = float(self.get_current_price_data()['last'])
				print(f'Current Price: ${latest}')
				# Check how price has changed 
				dPrice = int(self.price - latest)
				print('Delta: %d' % dPrice)
				self.price = latest

				if dPrice <= -100:
					# send message that BTC Price has gone up by atleast $50 
					msg = f'<@&{CRYPTO_ROLE}> *BTC Price risen* up to  **${latest}**'
					DiscordMsg('text',{'content':msg}).send_message()
				elif dPrice >= 100:
					msg = f'<@&{CRYPTO_ROLE}> *BTC Price slipped* down to  **${latest}**'
					DiscordMsg('text',{'content':msg}).send_message()
			except KeyboardInterrupt:
				self.running = False
				pass


def main():
	cb = CryptoBot()
	cb.run()


if __name__ == '__main__':
	main()