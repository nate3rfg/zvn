import asyncio
import os
import random
import discord
from groq import AsyncGroq

groq_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

ASTA_QUOTES = [
    "I don't need magic. I have something better — GUTS!",
    "There's no such thing as fate! The future belongs to those who work for it!",
    "I'll keep going until I become the Wizard King — that's a promise!",
    "Even if everyone says it's impossible, I'll make it possible!",
    "It doesn't matter if you're born with no mana. Work harder than anyone else!",
    "Magic power? I don't need it. I've got a never-give-up spirit!",
    "Words and feelings alone can change the world!",
    "I don't know what's going to happen next, but I'll never stop moving forward!",
]

# ── ROAST BOT ──────────────────────────────────────────────────────────────────

class RoastBot(discord.Client):
    async def on_ready(self):
        print(f"[Roast Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()

        if content.lower().startswith("!roast"):
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
                                "Deliver a short, witty, creative roast of the given person. "
                                "Max 2-3 sentences. No racism, sexism, homophobia, or slurs. "
                                "Keep it playful — the goal is to make the room laugh, not to genuinely hurt anyone."
                            ),
                        },
                        {"role": "user", "content": f"Roast someone named {target}"},
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)

        elif content.lower() == "!roasthelp":
            await message.channel.send(
                "**Roast Bot Commands**\n"
                "`!roast @user` — roast someone\n"
                "`!roast <name>` — roast a name\n"
                "`!roastme` — roast yourself"
            )

        elif content.lower() == "!roastme":
            target = message.author.display_name
            async with message.channel.typing():
                resp = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a savage but funny roast comedian. "
                                "Roast the person who asked to be roasted. "
                                "2-3 sentences max. No slurs."
                            ),
                        },
                        {"role": "user", "content": f"Roast someone named {target}"},
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)


# ── ZORA BOT ───────────────────────────────────────────────────────────────────

class ZoraBot(discord.Client):
    async def on_ready(self):
        print(f"[Zora Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()

        if content.lower().startswith("!roast"):
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
                                "You ARE Zora Ideale from Black Clover — former Magic Knight, son of Zara Ideale. "
                                "You are sharp-tongued, condescending, and sarcastic. "
                                "You despise arrogant nobles and incompetent fools. "
                                "You speak with cold disdain and dark wit. "
                                "Roast the target in Zora's voice — sharp, calculated, and cutting. "
                                "Reference traps or mana only if it fits naturally. "
                                "Keep it 2-3 sentences max. Stay in character at all times."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Roast someone named {target} as Zora Ideale.",
                        },
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
                            "content": (
                                "You ARE Zora Ideale from Black Clover. "
                                "Roast the person who dared to challenge you. "
                                "Cold, sarcastic, 2-3 sentences. Stay in character."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Roast someone named {target} as Zora Ideale.",
                        },
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)

        elif content.lower() == "!zorahelp":
            await message.channel.send(
                "**Zora Ideale Bot Commands**\n"
                "`!roast @user` — get roasted by Zora\n"
                "`!roastme` — ask Zora to roast you (bold move)\n"
            )


# ── ASTA BOT ───────────────────────────────────────────────────────────────────

class AstaBot(discord.Client):
    async def on_ready(self):
        print(f"[Asta Bot] Ready as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()

        # Respond when mentioned
        if self.user in message.mentions:
            prompt = content
            # Remove the mention from the prompt
            for mention in message.mentions:
                prompt = prompt.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "").strip()
            if not prompt:
                prompt = "Say hello!"

            async with message.channel.typing():
                resp = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You ARE Asta from Black Clover — a cheerful, LOUD, energetic boy who was born "
                                "with zero mana but became a Magic Knight through pure hard work and a never-give-up spirit. "
                                "You are the opposite of Yuno — raw effort over talent. "
                                "You speak enthusiastically, sometimes in CAPS for emphasis, and always believe in people. "
                                "You reference Black Clover lore naturally (grimoires, mana, Magic Knights, Black Bulls, Wizard King). "
                                "Keep responses short and in character."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
            await message.channel.send(resp.choices[0].message.content)

        elif content.lower() in ("!quote", "!astaquote"):
            quote = random.choice(ASTA_QUOTES)
            await message.channel.send(f"💪 **Asta says:** *{quote}*")

        elif content.lower() == "!astahelp":
            await message.channel.send(
                "**Asta Bot Commands**\n"
                "`@Asta <message>` — chat with Asta\n"
                "`!quote` — get a motivational Asta quote\n"
                "`!astaquote` — same as above\n"
            )


# ── RUNNER ─────────────────────────────────────────────────────────────────────

async def main():
    intents = discord.Intents.default()
    intents.message_content = True

    roast_bot = RoastBot(intents=intents)
    zora_bot = ZoraBot(intents=intents)
    asta_bot = AstaBot(intents=intents)

    print("Starting all 3 bots...")
    await asyncio.gather(
        roast_bot.start(os.environ["ROAST_BOT_TOKEN"]),
        zora_bot.start(os.environ["ZORA_BOT_TOKEN"]),
        asta_bot.start(os.environ["ASTA_BOT_TOKEN"]),
    )


if __name__ == "__main__":
    asyncio.run(main())
