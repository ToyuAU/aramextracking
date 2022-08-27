import requests
from bs4 import BeautifulSoup
from discord_webhook import *
import time
import datetime
import random
from colored_log.colored_log import LOG

runs = 0
delay = 600
data = {}
first_run = True
proxies = []

def proxy():
    proxy = random.choice(proxies)
    IP, PORT, USER, PASS = proxy.split(':')
    return {'http': 'http://{}:{}@{}:{}'.format(USER, PASS, IP, PORT), 'https': 'http://{}:{}@{}:{}'.format(USER, PASS, IP, PORT)}

def webhook(activity):
    try:
        webhook = DiscordWebhook(url='')
        embed = DiscordEmbed(title='Aramex Tracking', description='`New Activity`', url='https://www.aramex.com/au/en/track/results?ShipmentNumber=34151885460', color=0x000000)
        for datatype in activity.find_all('td'):
            if datatype.attrs['data-heading'] == 'Date':
                embed.add_embed_field(name='**Time**', value=datatype.text.strip(), inline=False)
            elif datatype.attrs['data-heading'] == 'Location':
                embed.add_embed_field(name='**Location**', value=datatype.text.strip(), inline=False)
            elif datatype.attrs['data-heading'] == 'Activity':
                embed.add_embed_field(name='**Activity**', value=datatype.text.strip(), inline=False)
        embed.set_timestamp()
        embed.set_footer(text='Aramex Tracking', icon_url='https://iconape.com/wp-content/files/dt/380443/png/380443.png')
        webhook.add_embed(embed)
        webhook.execute()
    except Exception as e:
        print(e)
        LOG('Failed to send webhook...', 'red')



def main():
    global runs, delay, data, first_run
    while True:
        runs += 1
        if runs <= 5 or runs % 500 == 0:
            LOG('Monitor Alive! Run: {}'.format(runs), 'blue')

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.aramex.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.aramex.com/au/en',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'
        }
        try:
            r = requests.get('https://www.aramex.com/au/en/track/results?ShipmentNumber=', headers=headers, proxies=proxy())
        except:
            LOG('Failed to get site...', 'red')
            time.sleep(delay)
            continue

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for activity in soup.find_all('tr'):
                for datatype in activity.find_all('td'):
                    if datatype.attrs['data-heading'] == 'Date':
                        if datatype.text.strip() not in data:
                            data[datatype.text.strip()] = True
                            LOG('New activity found!', 'green')
                            if not first_run:
                                webhook(activity)

        else:
            LOG('Bad status code... Got: '+str(r.status_code), 'red')
        
        time.sleep(delay)
        first_run = False


main()