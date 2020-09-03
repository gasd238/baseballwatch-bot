import requests
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import bs4
import time
import discord
import datetime
from key import *


loop = asyncio.get_event_loop()

client = discord.Client()
chrdir = '../chromedriver.exe'
teamrank = []
now = datetime.datetime.now()
weekend_string = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

chrome_options = Options()
chrome_options.add_argument("--headless --log-level=OFF")

#Discord Client
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------------------')
    game = discord.Game("!설명으로 도움말")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    channel = message.channel
    if message.author.bot:
        return None

    if message.content == '!설명':
        help_ = discord.Embed(title = '설명', description = '야구 시청 봇 설명')
        help_.add_field(name='!야구', value='야구 중계를 불러옵니다.(다음 스포츠 야구 문자 중계 링크 필수 네이버 안됨)', inline=False)
        await channel.send(embed = help_)

    if message.content == '!야구':
        await channel.send('볼 야구경기의 다음 스포츠 문자중계 주소를 입력해 주세요')
        def check(m):
            return m.channel == channel
        url = await client.wait_for('message', check=check)
        driver = webdriver.Chrome(chrdir, chrome_options=chrome_options)
        if url.content.startswith('http'):
            driver.get(url.content)
        else:
            await channel.send('처음부터 다시 시작해 주세요')
            return None
        loop.create_task(realtime(driver, channel))
    
    if message.content.startswith('!순위'):
        req = requests.get("http://www.statiz.co.kr/main.php").text
        soup = bs4.BeautifulSoup(req, 'lxml')
        box = soup.find('table', class_='table table-striped')
        wa = box.find_all('div', class_='badge')
        for i in wa:
            teamrank.append(i.getText())
        await channel.send('**'+str(now.year)+'년 '+str(now.month)+'월 '+str(now.day)+'일 '+ str(weekend_string[int(now.weekday())]) +' 순위' + '**')
        for i in range(10):
            await channel.send(str(i+1)+'위 '+teamrank[i])
        


async def realtime(driver, channel): 
    smsli = []
    teamname = []
    teamscore = []
    teamlogo = []
    linum = -1
    while True:
        soup = bs4.BeautifulSoup(driver.page_source, 'lxml')            
        inn = soup.find('span', class_="txt_inning").getText()
        temp = soup.find('div', class_='sms_list')
        sms = soup.find_all(class_='sms_word')
        inning = soup.find('span', class_='txt_inning')
        soups = soup.find_all('span', class_='inner_team')
        try:
            final = soup.find('div', class_='gc_cont gc_result')
            pitfinal = final.find('div', class_='cont_result')
        except:
            pass
        
        for i in soups:
            teamname.append(i.find_all('span', class_='txt_team'))
            teamscore.append(i.find_all('span', class_='screen_out'))
            teamlogo.append(i.find_all('img', class_='thumb_g img_logo'))

        sms.reverse()

        for i in range(len(sms)):
            if inning.getText() in sms[i].getText():
                sms = sms[i:]
                break

        for smstext in sms:
            try:
                if smstext in smsli[linum]:
                    continue
                else:
                    if '공격' in smstext.getText() or '경기종료' in smstext.getText() or '타자' in smstext.getText():
                        team1 = discord.Embed(title = teamname[0][0].getText(), description = teamscore[0][0].getText())
                        team1.set_thumbnail(url = 'http:'+teamlogo[0][0].attrs['src'])
                        team2 = discord.Embed(title = teamname[1][0].getText(), description = teamscore[1][0].getText())
                        team2.set_thumbnail(url = 'http:'+teamlogo[1][0].attrs['src'])
                        await channel.send("**" + smstext.getText() + "**")
                        if '타자' not in smstext.getText():
                            await channel.send(embed = team1)
                            await channel.send(embed = team2)
                    else:
                        await channel.send(smstext.getText())
                        time.sleep(2)
            except IndexError:
                if '공격' in smstext.getText() or '경기종료' in smstext.getText() or '타자' in smstext.getText():
                    team1 = discord.Embed(title = teamname[0][0].getText(), description = teamscore[0][0].getText())
                    team1.set_thumbnail(url = 'http:'+teamlogo[0][0].attrs['src'])
                    team2 = discord.Embed(title = teamname[1][0].getText(), description = teamscore[1][0].getText())
                    team2.set_thumbnail(url = 'http:'+teamlogo[1][0].attrs['src'])
                    await channel.send("**" + smstext.getText() + "**")
                    if '타자' not in smstext.getText():
                        await channel.send(embed = team1)
                        await channel.send(embed = team2)
                    if '경기종료' in smstext.getText() and pitfinal != None:
                        pitname = pitfinal.find_all('dt', class_='tit_name')
                        pitface = pitfinal.find_all('img', class_='thumb_g')
                        pitresult = pitfinal.find_all('span', class_='txt_gc')
                        for i in range(0, len(pitname)):
                            pit = discord.Embed(title=pitname[i].getText(), description=pitresult[i].getText())
                            pit.set_thumbnail(url = 'http:'+ pitface[i].attrs['src'])
                            await channel.send(embed = pit)
                else:
                    await channel.send(smstext.getText())
                    time.sleep(2)
        
        smsli.append(sms)
        linum+=1
        sms.reverse()
        if sms[0].getText() == '경기종료':
            loop.stop(realtime(driver, channels))
            break    
        time.sleep(5) 
    
client.run(key)
