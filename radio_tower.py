import discord
import discord.app_commands
import random
import math
import MySQLdb
from dotenv import load_dotenv
import os

load_dotenv()


client = discord.Client(intents=discord.Intents.default())
token = os.environ.get("Bot_Token")
tree = discord.app_commands.CommandTree(client)
increace_point = 30
require_point = 45

def mysql_connect():
    connection = MySQLdb.connect(
        user = "root",
        passwd = "061210",
        host = "localhost",
        db = "radio_tower"
    )
    cursor = connection.cursor()  #カーソル
    return connection, cursor




@tree.command(
    name = "transmit",
    description = "電波塔に向けて信号を送ります"
)
async def transmit(interaction:discord.Interaction,arg1:str):
    if len(arg1) < 256:

        connection,cursor = mysql_connect()
        connection  #接続

        stmt = "insert into messages (content) values (%s)"
        cursor.execute(stmt,(arg1,))
        connection.commit()

        user_id = interaction.user.id
        stmt = "select * from points where id = %s"
        cursor.execute(stmt,(user_id,))
        result = cursor.fetchall()

        if len(result) == 0:
            stmt = "insert into points (id,point) values (%s,%s)"
            cursor.execute(stmt,(user_id,increace_point))
            connection.commit()
        else:
            result_id = result[0][0]
            current_point = result[0][1]
            stmt = "update points set point=point+%s where id=%s"
            cursor.execute(stmt,(increace_point,result_id))
            connection.commit()

            cursor.close()
            connection.close()

            embed = discord.Embed(title = "送信完了",description = "送信内容："+arg1,color=0x00ff00)
            embed.add_field(name="現在のポイント",value=current_point+increace_point)
            await interaction.response.send_message(embed = embed,ephemeral=True)
            
    else:
        embed = discord.Embed(title = "エラー",description = "文字数は255文字以下にしてください",color=0xFF0000)
        await interaction.response.send_message(embed = embed,ephemeral=True)



@tree.command(
    name = "recieve",
    description = "電波塔から信号を受信します"
)
async def recieve(interaction:discord.Interaction):
    connection,cursor = mysql_connect()
    connection

    user_id = interaction.user.id
    stmt = "select * from radio_tower.points where id = %s"

    cursor.execute(stmt,(user_id,))
    result = cursor.fetchall()



    if len(result)==0:
        embed = discord.Embed(title = "エラー",description="ポイントがありません！メッセージを送ってポイントを貯めましょう！",color = 0xFF0000)
        cursor.close()
        connection.close()
        await interaction.response.send_message(embed=embed)

    else:
        current_point = result[0][1]
        if current_point < require_point:
            embed = discord.Embed(title = "エラー",description="ポイントが足りません！メッセージを送ってポイントを貯めましょう！",color = 0xFF0000)
            embed.add_field(name="現在のポイント",value=result[0][1])
            
            cursor.close()
            connection.close()
            await interaction.response.send_message(embed = embed)
        else:

            stmt = "select * from radio_tower.messages"
            cursor.execute(stmt)
            result = cursor.fetchall()
            result_length = len(result)
            randomInt = math.floor(random.random()*(result_length))



            if result_length == 0:
                embed = discord.Embed(title = "エラー",description="メッセージが見つかりませんでした・・・",color = 0xFF0000)
                cursor.close()
                connection.close()
                await interaction.response.send_message(embed = embed)
                
            else:
                recieveId = result[randomInt][0]
                recieveMessage = result[randomInt][1]

                embed = discord.Embed(title="受信成功！", description=recieveMessage,color = 0x00ff00)
                embed.add_field(name="現在のポイント",value=current_point-require_point)

                stmt = "delete from messages where id = %s"
                cursor.execute(stmt,(recieveId,))
                connection.commit()

                stmt = "update points set point=point-%s where id=%s"
                cursor.execute(stmt,(require_point,user_id))
                connection.commit()

                cursor.close()
                connection.close()
                await interaction.response.send_message(embed = embed)

@tree.command(
    name = "point",
    description="現在の保有ポイントを表示します"
)
async def get_point(interaction:discord.Interaction):
    connection,cursor = mysql_connect()
    connection

    user_id = interaction.user.id

    stmt = "select * from points where id = %s"
    cursor.execute(stmt,(user_id,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    if len(result) == 0:
        embed = discord.Embed(title = "現在のポイント",description = 0,color = 0x00FF00)
    else:
        current_point = result[0][1]
        embed = discord.Embed(title = "現在のポイント",description = current_point,color = 0x00FF00)
        
    await interaction.response.send_message(embed = embed)



@tree.command(
    name = "help",
    description = "ヘルプを表示します"
)
async def help(interaction:discord.Interaction):
    embed = discord.Embed(
        title = "ヘルプ",
        description = "コマンドのヘルプです。",
        color = 0x00FFFF
    )
    embed.add_field(name = "/transmit ```arg1```", value = f"電波塔に向けて信号を送ります。一回ごとに{increace_point}ポイント取得できます。", inline = False)
    embed.add_field(name = "/recieve", value = f"電波塔から信号を受信します。一回ごとに{require_point}ポイント必要です。",inline = False)
    embed.add_field(name = "/point", value = "現在保有しているポイントを表示します。",inline=False)
    embed.add_field(name = "/help", value = "このヘルプを表示します。", inline =False)
    
    await interaction.response.send_message(embed = embed)

@client.event
async def on_ready():
    print("Discord.py Version:"+discord.__version__)
    print(f"{client.user} にログインしました")
    await tree.sync()


client.run(token)