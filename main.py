from keep_alive import keep_alive
import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 自己紹介チャンネルとロールの設定 ---
SELF_INTRO_CHANNEL_ID = 1358706146067878009  # 自己紹介チャンネルID
ROLE_ID_TO_GIVE = 1359197668303179836        # 自己紹介で付与するロールID

# --- ロール選択ボタン設定（最大2つまで） ---
ROLE_IDS = {
    "beginner": 1359052232636502047,
    "advanced": 1359052588267343963,
    "jp": 1359053638646890679,
    "en": 1359054018521071769,
    "silent": 1359475959199305758
}

ROLE_INFO = {
    "beginner": {
        "label": "Beginner / 初心者",
        "add": "You’ve joined the Beginner group! 言語学習を始めたばかりの人っすね、ようこそぽへ〜！",
        "remove": "You’ve left the Beginner group. また戻ってきてほしいっすにょ〜！"
    },
    "advanced": {
        "label": "Advanced / 上級者",
        "add": "You’ve joined the Advanced group! 学びを深めたい気持ち、すちすちっす！",
        "remove": "You’ve left the Advanced group. また一緒に学べる日を楽しみにしてるっすにょ〜！"
    },
    "jp": {
        "label": "JP Speaker / 日本語話者",
        "add": "You’ve joined the JP Speaker group! 日本語が得意な人っすね、にゃふ〜！",
        "remove": "You’ve left the JP Speaker group. またお話できると嬉しいっすにょ〜！"
    },
    "en": {
        "label": "EN Speaker / 英語話者",
        "add": "You’ve joined the EN Speaker group! 英語が得意なんて、すごいっすにょ！",
        "remove": "You’ve left the EN Speaker group. また英語でおしゃべりしましょ〜！"
    },
    "silent": {
        "label": "Silent Observer / ロム専",
        "add": "You’ve joined as a Silent Observer. 見るだけ・聞くだけの静かな仲間も大歓迎っす！",
        "remove": "You’ve left the Silent Observer role. またこっそり来てにゃ〜！"
    }
}

MAX_ROLES = 2  # 選べる最大数

# ------------------- イベント処理 --------------------

@bot.event
async def on_ready():
    print(f"{bot.user} でログインしたにゃ！")
    bot.add_view(RoleView())  # ← これがないと既存のボタンは無効のまま！

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == SELF_INTRO_CHANNEL_ID:
        role = message.guild.get_role(ROLE_ID_TO_GIVE)
        if role:
            if role not in message.author.roles:
                await message.author.add_roles(role)
                await message.channel.send(
                    f"{message.author.mention}, thanks for your lovely intro! You can now hop into <#1359199564636361036>.\n"
                    f"自己紹介ありがとうっす！ <#1359199564636361036> にアクセスできるようになったっすにょ！"
                )
            else:
                await message.channel.send(
                    f"{message.author.mention}, looks like you've already got the role,ぽへ〜！\n"
                    f"もうロール持ってるっすにょ〜！"
                )
        else:
            await message.channel.send(
                f"{message.author.mention}, oops… I couldn't find the role. It might be a setup issue, sorry!\n"
                f"にゃっ！？ロールが見つからなかったにょ……設定ミスかもしれないっす。"
            )

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(
            f"Welcome to na²lingua, {member.mention}!\n"
            "Please take a moment to read the pinned message in this channel before heading over to <#1358706146067878009>. We're so happy to have you hereぽへ〜！\n\n"
            "na²linguaへようこそっすにょ！\n"
            "このチャンネルにピン留めしてある説明事項をよく読んでから、<#1358706146067878009>へ向かってほしいっす！\n"
        )

# ------------------- ロール選択ボタン --------------------

class RoleButton(Button):
    def __init__(self, role_key):
        super().__init__(
            label=ROLE_INFO[role_key]["label"],
            style=discord.ButtonStyle.secondary,  # ← 全部紫グレーにしたにゃ！
            custom_id=role_key
        )
        self.role_key = role_key

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(ROLE_IDS[self.role_key])

        current_roles = [guild.get_role(rid) for rid in ROLE_IDS.values() if guild.get_role(rid) in member.roles]

        if role in current_roles:
            await member.remove_roles(role)
            await interaction.response.send_message(ROLE_INFO[self.role_key]["remove"], ephemeral=True)
        else:
            if len(current_roles) >= MAX_ROLES:
                await interaction.response.send_message(
                    f"You can only choose up to {MAX_ROLES} roles! 選べるのは最大{MAX_ROLES}個までっすにょ〜！",
                    ephemeral=True
                )
            else:
                await member.add_roles(role)
                await interaction.response.send_message(ROLE_INFO[self.role_key]["add"], ephemeral=True)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for key in ROLE_IDS.keys():
            self.add_item(RoleButton(key))

@bot.command()
async def send_roles(ctx):
    view = RoleView()
    await ctx.send("Please select your roles below! 下からロールを選んでぽへ〜（最大2つまで）", view=view)

keep_alive()

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

