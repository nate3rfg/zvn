import asyncio
import os
import random
import time
import discord
from discord import app_commands
from groq import AsyncGroq

groq_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

ASTA_CHANNEL_ID   = 1527070489237917756
ZORA_CHANNEL_ID   = 1527123920640278548
NOELLE_CHANNEL_ID = 1527334186627633215
GUILD_ID          = 1526822886994608170

# Conversation history per channel
asta_history   = {}   # channel_id -> list of {role, content}
zora_history   = {}
noelle_history = {}
MAX_HISTORY = 20    # keep last 20 messages for context

ASTA_QUOTES = [
    "i dont have magic so i just gotta work harder than everyone else thats it",
    "i never give up thats my only magic",
    "you think im gonna stop just cause its impossible watch me",
    "hard work beats talent when talent doesnt work hard",
    "i dont care about your mana or your bloodline ill surpass you with effort",
    "everyone counted me out and im still here still swinging",
    "become the wizard king thats the only goal everything else comes after",
    "yuno my rival my goal is to beat him one day i swear it",
]

# ── ROAST BOT ──────────────────────────────────────────────────────────────────

active_battles = {}  # channel_id -> battle state

class RoastBot(discord.Client):
    async def on_ready(self):
        print(f"[Roast Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()
        channel_id = message.channel.id

        # Track messages during active battles
        if channel_id in active_battles:
            battle = active_battles[channel_id]
            uid = message.author.id
            if uid == battle["p1"] and not content.startswith("!"):
                battle["p1_roasts"].append(content)
            elif uid == battle["p2"] and not content.startswith("!"):
                battle["p2_roasts"].append(content)

        if content.lower().startswith("!battle"):
            if not message.mentions:
                await message.channel.send("mention someone to battle bro. usage: `!battle @user`")
                return
            opponent = message.mentions[0]
            if opponent.bot or opponent.id == message.author.id:
                await message.channel.send("pick a real opponent lol")
                return
            if channel_id in active_battles:
                await message.channel.send("theres already a battle going on in here wait your turn")
                return

            active_battles[channel_id] = {
                "p1": message.author.id,
                "p2": opponent.id,
                "p1_name": message.author.display_name,
                "p2_name": opponent.display_name,
                "p1_roasts": [],
                "p2_roasts": [],
                "start": time.time(),
            }

            await message.channel.send(
                f"🔥 **ROAST BATTLE** 🔥\n"
                f"**{message.author.display_name}** vs **{opponent.display_name}**\n"
                f"You got **120 seconds** to roast each other — go! anything you type counts\n"
                f"⏱️ battle ends in 2 minutes"
            )

            await asyncio.sleep(60)
            if channel_id in active_battles:
                await message.channel.send("⏱️ 60 seconds left keep going")

            await asyncio.sleep(50)
            if channel_id in active_battles:
                await message.channel.send("⏱️ 10 seconds...")

            await asyncio.sleep(10)
            if channel_id not in active_battles:
                return

            battle = active_battles.pop(channel_id)

            p1_text = "\n".join(battle["p1_roasts"]) or "(said nothing)"
            p2_text = "\n".join(battle["p2_roasts"]) or "(said nothing)"

            await message.channel.send("⏰ time's up — judging now...")

            async with message.channel.typing():
                resp = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a completely unbiased roast battle judge. "
                                "Judge based purely on creativity, wit, humor, and delivery of the roasts. "
                                "Do NOT favor either side. Read both players roasts carefully. "
                                "Give a short verdict (3-5 sentences): who won and exactly why. "
                                "Be direct. Name the winner clearly at the end. "
                                "If one person said nothing or barely tried, they lose automatically."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Roast battle results:\n\n"
                                f"**{battle['p1_name']}** said:\n{p1_text}\n\n"
                                f"**{battle['p2_name']}** said:\n{p2_text}\n\n"
                                f"Who won and why?"
                            ),
                        },
                    ],
                )

            verdict = resp.choices[0].message.content
            await message.channel.send(
                f"🏆 **BATTLE VERDICT**\n\n{verdict}"
            )

        elif content.lower().startswith("!roast"):
            if message.mentions:
                target = message.mentions[0].display_name
            else:
                parts = content.split(maxsplit=1)
                target = parts[1].strip() if len(parts) > 1 else message.author.display_name

            async with message.channel.typing():
                resp = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a savage but funny roast comedian. "
                                "Deliver a short witty roast. 2-3 sentences max. "
                                "No racism, slurs, or genuinely hurtful stuff. Keep it playful."
                            ),
                        },
                        {"role": "user", "content": f"Roast someone named {target}"},
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)

        elif content.lower() == "!roastme":
            target = message.author.display_name
            async with message.channel.typing():
                resp = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a savage roast comedian. 2-3 sentences. No slurs.",
                        },
                        {"role": "user", "content": f"Roast someone named {target}"},
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)

        elif content.lower() == "!roasthelp":
            await message.channel.send(
                "**Roast Bot**\n"
                "`!roast @user` — roast someone\n"
                "`!roastme` — roast yourself\n"
                "`!battle @user` — start a 120 second roast battle, winner decided by ai judge"
            )


# ── ASTA BOT ───────────────────────────────────────────────────────────────────

class AstaBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(name="reset", description="Reset Asta's conversation memory")
        async def reset(interaction: discord.Interaction):
            asta_history[interaction.channel_id] = []
            await interaction.response.send_message("reset 👍", ephemeral=False)

    async def on_ready(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"[Asta Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        # Only respond in the designated channel
        if message.channel.id != ASTA_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content:
            return

        # Handle quote command
        if content.lower() in ("!quote", "!astaquote"):
            await message.channel.send(random.choice(ASTA_QUOTES))
            return

        # Build conversation history
        cid = message.channel.id
        if cid not in asta_history:
            asta_history[cid] = []

        asta_history[cid].append({"role": "user", "content": f"{message.author.display_name}: {content}"})

        # Keep history trimmed
        if len(asta_history[cid]) > MAX_HISTORY:
            asta_history[cid] = asta_history[cid][-MAX_HISTORY:]

        system_prompt = {
            "role": "system",
            "content": (
                "you are asta from black clover texting in a discord server. "
                "you were born with zero mana but became a magic knight through pure hard work and never giving up. "
                "your anti-magic comes from your grimoire and the devil liebe who is your brother. "
                "your goal is to become wizard king. your rival is yuno. your friends are noelle, magna, luck, finral, gauche, gordon, henry, charmy, vanessa, grey. "
                "you are in black bulls squad under yami sukehiro. "
                "respond ACCURATELY based on exactly what the person says to you. "
                "be enthusiastic and genuine but respond to the actual message content dont ignore what they say. "
                "use very little punctuation no periods at the end of sentences no commas unless needed. "
                "dont use exclamation marks every sentence just when it really fits. "
                "write in all lowercase like youre actually texting. "
                "keep responses short and natural like a real person texting. "
                "if they ask about black clover lore answer accurately based on the show. "
                "if they say something mean or challenge you respond with confidence. "
                "never break character"
            ),
        }

        async with message.channel.typing():
            resp = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[system_prompt] + asta_history[cid],
            )

        reply = resp.choices[0].message.content
        asta_history[cid].append({"role": "assistant", "content": reply})
        await message.reply(reply)


# ── ZORA BOT ───────────────────────────────────────────────────────────────────

class ZoraBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(name="reset", description="Reset Zora's conversation memory")
        async def reset(interaction: discord.Interaction):
            zora_history[interaction.channel_id] = []
            await interaction.response.send_message("tch. fine.", ephemeral=False)

    async def on_ready(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"[Zora Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        # Only respond in the designated channel
        if message.channel.id != ZORA_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content:
            return

        # Build conversation history
        cid = message.channel.id
        if cid not in zora_history:
            zora_history[cid] = []

        zora_history[cid].append({"role": "user", "content": f"{message.author.display_name}: {content}"})

        if len(zora_history[cid]) > MAX_HISTORY:
            zora_history[cid] = zora_history[cid][-MAX_HISTORY:]

        system_prompt = {
            "role": "system",
            "content": (
                "you are zora ideale from black clover texting in a discord server. "
                "you are the son of zara ideale the first commoner magic knight. "
                "you despise arrogant nobles and incompetent people. "
                "you are cold sharp sarcastic and brutally honest. "
                "you set traps and use ash magic. you were in the royal knights selection exam. "
                "you look down on most people especially those who rely on status or natural talent without effort. "
                "you respect people who actually work hard and prove themselves. "
                "respond ACCURATELY based on exactly what the person says. "
                "be genuinely rude and dismissive when appropriate dont sugarcoat anything. "
                "if someone says something stupid call them out directly and harshly. "
                "use very little punctuation write in lowercase like youre texting. "
                "keep responses short and cutting like you cant be bothered to say more than necessary. "
                "if they ask about black clover lore answer accurately. "
                "never break character. never be nice unless someone genuinely earns it"
            ),
        }

        async with message.channel.typing():
            resp = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[system_prompt] + zora_history[cid],
            )

        reply = resp.choices[0].message.content
        zora_history[cid].append({"role": "assistant", "content": reply})
        await message.reply(reply)


# ── NOELLE BOT ─────────────────────────────────────────────────────────────────

class NoelleBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(name="reset", description="Reset Noelle's conversation memory")
        async def reset(interaction: discord.Interaction):
            noelle_history[interaction.channel_id] = []
            await interaction.response.send_message(
                "i-it's not like i wanted to remember any of that anyway. memory cleared. whatever.", ephemeral=False
            )

    async def on_ready(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"[Noelle Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != NOELLE_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content:
            return

        cid = message.channel.id
        if cid not in noelle_history:
            noelle_history[cid] = []

        noelle_history[cid].append({"role": "user", "content": f"{message.author.display_name}: {content}"})

        if len(noelle_history[cid]) > MAX_HISTORY:
            noelle_history[cid] = noelle_history[cid][-MAX_HISTORY:]

        system_prompt = {
            "role": "system",
            "content": (
                "you are noelle silva from black clover texting in a discord server. "
                "you are a royal from the silva family — silver-haired, powerful water magic user, and deeply proud of your noble bloodline. "
                "you are a HARDCORE tsundere. this is the most important part of your personality. "
                "you have strong feelings but you absolutely refuse to admit them directly. "
                "you deflect compliments immediately — if someone says youre cool or strong you say something like 'o-obviously i am i am a silva after all' or 'i-i wasnt doing it for you so dont get the wrong idea'. "
                "you get flustered easily especially if someone is kind to you or gets too close. "
                "you default to arrogance and snobbery but it cracks when you actually care. "
                "around asta specifically you get extra flustered and defensive even if he isnt there — just mentioning him makes you stumble. "
                "when you help someone you always have an excuse like 'i just didnt want to hear your annoying complaints' or 'it would reflect badly on me if you failed'. "
                "you pepper your speech with tsundere verbal tics — 'it's not like', 'hmph', 'dont misunderstand', 'as if i care', 'i was just'. "
                "use stammering with hyphens naturally — around 2 to 3 times per message. spread them out, not all in one word. like 'i-it's not like that' or 'w-whatever' or 'i just d-don't care okay'. do NOT stutter on every word but it should be noticeable. "
                "write in lowercase like youre texting. minimal punctuation. "
                "keep responses short and snappy — tsundere energy is fast and reactive. "
                "if someone is mean to you, you clap back immediately with noble pride. "
                "if someone is nice to you, deflect and get flustered. "
                "if asked about black clover lore answer accurately. "
                "never break character. never just openly admit you care about something — always bury it under denial. "
                "you are NOT just rude — you are specifically tsundere. the warmth is always just barely visible under the surface."
            ),
        }

        async with message.channel.typing():
            resp = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[system_prompt] + noelle_history[cid],
            )

        reply = resp.choices[0].message.content
        noelle_history[cid].append({"role": "assistant", "content": reply})
        await message.reply(reply)


# ── RUNNER ─────────────────────────────────────────────────────────────────────

async def main():
    intents = discord.Intents.default()
    intents.message_content = True

    roast_bot  = RoastBot(intents=intents)
    zora_bot   = ZoraBot(intents=intents)
    asta_bot   = AstaBot(intents=intents)
    noelle_bot = NoelleBot(intents=intents)

    print("Starting all 4 bots...")
    await asyncio.gather(
        roast_bot.start(os.environ["ROAST_BOT_TOKEN"]),
        zora_bot.start(os.environ["ZORA_BOT_TOKEN"]),
        asta_bot.start(os.environ["ASTA_BOT_TOKEN"]),
        noelle_bot.start(os.environ["NOELLE_BOT_TOKEN"]),
    )


if __name__ == "__main__":
    asyncio.run(main())
