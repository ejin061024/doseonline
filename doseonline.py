import discord
import sqlite3
import time

achannel = '976244162712182859'

client = discord.Client()

def CalTime(s):
    hours = s // 3600
    s = s - hours*3600
    mu = s // 60
    ss = s - mu*60
    return str(hours) + '시간 ' + str(mu) + '분 ' + str(ss) + '초'

def ChkTime(s):
    hours = s // 3600
    s = s - hours*3600
    mu = s // 60
    return mu >= 30

@client.event
async def on_connect():
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        name TEXT,
        id TEXT,
        yn TEXT,
        stime TEXT
        )
    ''')
    print("출퇴근봇 ONLINE")
    game = discord.Game('!명령어')
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.content == '!명령어':
        embed = discord.Embed(title='명령어', description='!출근\n!퇴근')
        await message.channel.send(embed=embed)
        
    if message.content.startswith("!등록") and not message.content == '!등록여부':
        if message.author.guild_permissions.administrator and (message.author.id == 652762094147469332) or (message.author.id == 668174307041476631) or (message.author.id == 759681094001229856) or (message.author.id == 680201159264567298):
            try:
                target = message.mentions[0]
            except:
                await message.channel.send('유저가 지정되지 않았습니다')

            try:
                db = sqlite3.connect('main.db')
                cursor = db.cursor()
                cursor.execute(f'SELECT yn FROM main WHERE id = {target.id}')
                result = cursor.fetchone()
                if result is None:
                    sql = 'INSERT INTO main(name, id, yn, stime) VALUES(?,?,?,?)'
                    val = (str(target), str(target.id), str('0'), str('0'))
                else:
                    embed = discord.Embed(title='❌  등록 실패', description='이미 등록된 유저입니다', color=0xFF0000)
                    await message.channel.send(embed=embed)
                    return
                cursor.execute(sql, val)
                db.commit()
                db.close()

                embed = discord.Embed(title='✅  등록 성공', description=f'등록을 성공하였습니다', colour=discord.Colour.green())
                embed.set_author(name=target, icon_url=target.avatar_url)
                await message.channel.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                await message.channel.send(embed=embed)
        else:
            await message.channel.send(f'{message.author.mention} 권한이 부족합니다')

    if message.content == '!등록여부':
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
        result = cursor.fetchone()
        if result is None:
            await message.channel.send(f'**{message.author}**님은 등록되지 않았습니다')
        else:
            await message.channel.send(f'**{message.author}**님은 등록되어 있습니다')

    if message.content == "!출근":
        try:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
            result = cursor.fetchone()
            if result is None:
                await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                return
            if "y" in result:
                await message.channel.send(f'{message.author.mention} 이미 출근 상태입니다')
                return
            else:
                sql = f'UPDATE main SET yn = ? WHERE id = {message.author.id}'
                val = (str('y'),)
                cursor.execute(sql, val)
                sql = f'UPDATE main SET stime = ? WHERE id = {message.author.id}'
                val = (str(time.time()),)
                cursor.execute(sql, val)
            db.commit()
            db.close()

            embed = discord.Embed(title='', description=f'**{message.author.mention}** 님이 출근하였습니다',
                                  color=discord.Colour.green())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text='출근시간: ' + time.strftime('%m-%d %H:%M'))
            await client.get_channel(int(achannel)).send(embed=embed)
            await message.channel.send(f'{message.author.mention} 출근완료')
        except Exception as e:
            embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
            await message.channel.send(embed=embed)

    if message.content.startswith("!조회"):
            targetid = 0
            try:
                author = message.mentions[0]
                targetid = author.id
            except IndexError:
                author = message.author
                targetid = author.id
            
                
            totalr = open('data.txt', 'r', encoding='UTF8')
            line = totalr.readlines()
            target = None
            for i in line:
                tmp = i.replace('\n', '')
                usri = tmp.split(":")
                if int(usri[0]) == targetid:
                    target = int(usri[1])
            if target == None:
                await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                return 

            embed = discord.Embed(title='', description=f'**{author}** 님의 누적 근무시간 : ' + CalTime(target),
                                  color=discord.Colour.green())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

    if message.content == "!전체조회":
        try:
            if message.author.guild_permissions.administrator and (message.author.id == 652762094147469332) or (message.author.id == 668174307041476631) or (message.author.id == 759681094001229856) or (message.author.id == 680201159264567298):
                totalr = open('data.txt', 'r', encoding='UTF8')
                line = totalr.readlines()
                target = ""
                for i in line:
                    tmp = i.replace('\n', '')
                    usri = tmp.split(":")
                    usrsr = await client.fetch_user(usri[0])
                    target += str(usrsr) + " : " + CalTime(int(usri[1])) + "\n"
                if target == "":
                    await message.channel.send(f'{message.author.mention} 데이터가 없습니다')
                    return 
                embed = discord.Embed(title='', description=target,
                                    color=discord.Colour.green())
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
        except Exception as e:
                embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                await message.channel.send(embed=embed)



    if message.content.startswith("!강제퇴근"):
        if message.author.guild_permissions.administrator and (message.author.id == 652762094147469332) or (message.author.id == 668174307041476631) or (message.author.id == 759681094001229856) or (message.author.id == 680201159264567298):
            targetid = 0
            try:
                author = message.mentions[0]
                targetid = author.id
            except IndexError:
                await message.channel.send(f'{message.author.mention} 유저를 찾을 수 없습니다')
                return
            try:
                db = sqlite3.connect('main.db')
                cursor = db.cursor()
                cursor.execute(f'SELECT yn FROM main WHERE id = {targetid}')
                result = cursor.fetchone()
                if result is None:
                    await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                    return
                else:

                    # if ChkTime(cctime) == False:
                    #     await message.channel.send(f'{message.author.mention} 퇴근불가\n현재 근무시간 : ' + CalTime(cctime))
                    #     return
                    if not "y" in result:
                        await message.channel.send(f'{message.author.mention} 출근상태가 아닙니다')
                        return
                    elif "y" in result:
                        cursor.execute(f'SELECT stime FROM main WHERE id = {targetid}')
                        result = cursor.fetchone()
                        result = str(result).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                        result = result.split(".")[0]
                        result = int(result)
                        cctime = round(time.time()) - result
                        sql = f'UPDATE main SET yn = ? WHERE id = {targetid}'
                        val = (str('n'),)
                        cursor.execute(sql, val)
                db.commit()
                db.close()
                
                totalr = open('data.txt', 'r', encoding='UTF8')
                isfound = False
                orig = ""
                line = totalr.readlines()
                for i in line:
                    tmp = i.replace('\n', '')
                    usri = tmp.split(":")
                    if int(usri[0]) == targetid:
                        isfound = True
                        orig += usri[0] + ":" + str(int(usri[1]) + cctime) + "\n"
                    else:
                        orig += tmp + "\n"
                if isfound == False:
                    print("등록되어있지 않은 유저")
                    orig += str(targetid) + ":" + str(cctime) + "\n"
                totalw = open('data.txt', 'w', encoding='UTF8')
                totalw.write(orig)
                totalw.close()
                print(cctime)

                embed = discord.Embed(title='', description=f'**{author}** 님이 **{message.author}**님에 의해 강제퇴근되었습니다',
                                    color=discord.Colour.red())
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                embed.set_footer(text='퇴근시간: ' + time.strftime('%m-%d %H:%M') + '\n' + '근무시간: ' + CalTime(cctime))
                await client.get_channel(int(achannel)).send(embed=embed)
                await message.channel.send(f'{message.author.mention} 퇴근완료')
            except Exception as e:
                    embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                    await message.channel.send(embed=embed)
    
    if message.content == "!퇴근":
        try:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
            result = cursor.fetchone()
            if result is None:
                await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                return
            else:

                # if ChkTime(cctime) == False:
                #     await message.channel.send(f'{message.author.mention} 퇴근불가\n현재 근무시간 : ' + CalTime(cctime))
                #     return
                if not "y" in result:
                    await message.channel.send(f'{message.author.mention} 출근상태가 아닙니다')
                    return
                elif "y" in result:
                    cursor.execute(f'SELECT stime FROM main WHERE id = {message.author.id}')
                    result = cursor.fetchone()
                    result = str(result).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                    result = result.split(".")[0]
                    result = int(result)
                    cctime = round(time.time()) - result
                    if ChkTime(cctime) == False:
                        await message.channel.send(f'{message.author.mention} 퇴근 불가\n현재 근무시간 :' + CalTime(cctime))
                        return
                    sql = f'UPDATE main SET yn = ? WHERE id = {message.author.id}'
                    val = (str('n'),)
                    cursor.execute(sql, val)
            db.commit()
            db.close()
            
            totalr = open('data.txt', 'r', encoding='UTF8')
            isfound = False
            orig = ""
            line = totalr.readlines()
            for i in line:
                tmp = i.replace('\n', '')
                usri = tmp.split(":")
                if int(usri[0]) == message.author.id:
                    isfound = True
                    orig += usri[0] + ":" + str(int(usri[1]) + cctime) + "\n"
                else:
                    orig += tmp + "\n"
            if isfound == False:
                print("등록되어있지 않은 유저")
                orig += str(message.author.id) + ":" + str(cctime) + "\n"
            totalw = open('data.txt', 'w', encoding='UTF8')
            totalw.write(orig)
            totalw.close()
            print(cctime)

            embed = discord.Embed(title='', description=f'**{message.author.mention}** 님이 퇴근하였습니다',
                                  color=discord.Colour.red())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text='퇴근시간: ' + time.strftime('%m-%d %H:%M') + '\n' + '근무시간: ' + CalTime(cctime))
            await client.get_channel(int(achannel)).send(embed=embed)
            await message.channel.send(f'{message.author.mention} 퇴근완료')
        except Exception as e:
                embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                await message.channel.send(embed=embed)

access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
