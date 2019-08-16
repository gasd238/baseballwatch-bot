import requests
from selenium import webdriver
import bs4
import time
import discord

client = discord.Client()

#Discord Client
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------------------')
    await client.change_presence(game=discord.Game(name="!설명으로 도움말", type=0))

@client.event
async def on_message(message):
    if message.author.bot:
        return None

    if message.content == '!설명':
        help_ = discord.Embed(title = '설명', description = '야구 시청 봇 설명')
        help_.add_field(name='!야구', value='야구 중계를 불러옵니다.(다음 스포츠 야구 문자 중계 링크 필수 네이버 안됨)', inline=false)
        await client.send_message(message.channel, embed = help_)
        
    if message.content == '!야구':
        await client.send_message(message.channel, '볼 야구경기의 다음 스포츠 문자중계 주소를 입력해 주세요')
        url = await client.wait_for_message(author=message.author, channel=message.channel)
        smsli = []
        teamname = []
        teamscore = []
        teamlogo = []
        linum = -1
        while True:
            chromedriver_dir = 'C:\chromedriver.exe'
            driver = webdriver.Chrome(chromedriver_dir)
            if url.content.startswith('http'):
                driver.get(url.content)
            else:
                await client.send_message(message.channel, '처음부터 다시 시작해 주세요')
                break
            soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
            driver.quit()
            
            inn = soup.find('span', class_="txt_inning").getText()
            temp = soup.find('div', class_='sms_list')
            sms = soup.find_all(class_='sms_word')
            inning = soup.find('span', class_='txt_inning')
            soups = soup.find_all('span', class_='inner_team')
            
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
                        if '공격' in smstext.getText() or '타자' in smstext.getText() or '경기 종료' in smstext.getText():
                            team1 = discord.Embed(title = teamname[0][0].getText(), description = teamscore[0][0].getText())
                            team1.set_image(url = 'http:'+teamlogo[0][0].attrs['src'])
                            team2 = discord.Embed(title = teamname[1][0].getText(), description = teamscore[1][0].getText())
                            team2.set_image(url = 'http:'+teamlogo[1][0].attrs['src'])
                            await client.send_message(message.channel, "**" + smstext.getText() + "**")
                            await client.send_message(message.channel, embed = team1)
                            await client.send_message(message.channel, embed = team2)
                        else:
                            await client.send_message(message.channel, smstext.getText())
                except IndexError:
                    if '공격' in smstext.getText() or '타자' in smstext.getText() or '경기 종료' in smstext.getText():
                        team1 = discord.Embed(title = teamname[0][0].getText(), description = teamscore[0][0].getText())
                        team1.set_image(url = 'http:'+teamlogo[0][0].attrs['src'])
                        team2 = discord.Embed(title = teamname[1][0].getText(), description = teamscore[1][0].getText())
                        team2.set_image(url = 'http:'+teamlogo[1][0].attrs['src'])
                        await client.send_message(message.channel, "**" + smstext.getText() + "**")
                        await client.send_message(message.channel, embed = team1)
                        await client.send_message(message.channel, embed = team2)
                    else:
                        team1 = discord.Embed(title = teamname[0][0].getText(), description = teamscore[0][0].getText())
                        team1.set_image(url = teamlogo[0][0].attrs['src'])
                        team2 = discord.Embed(title = teamname[1][0].getText(), description = teamscore[1][0].getText())
                        team2.set_image(url = teamlogo[1][0].attrs['src'])
                        await client.send_message(message.channel, smstext.getText())
            smsli.append(sms)
            linum+=1
            sms.reverse()
            if sms[0].getText() == '경기 종료':
                break
            time.sleep(20)
        
        
    
client.run('token')