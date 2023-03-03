import discord
import os
import requests
import io
import asyncio
import string
import time
import replicate
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import messages

os.environ['REPLICATE_API_TOKEN'] = '57b5717e8632693a79f0747038512564a640764c'
replicate_token = '57b5717e8632693a79f0747038512564a640764c'

client = discord.Client(intents=discord.Intents.all())
PREFIX = "/imagine"

@client.event
async def on_ready():
    print(
        'I am ready for listening.'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX + " "):
        await handle_input (message)

async def handle_input(message):
    prompt = message.content.split(PREFIX + " ")[1]
    if prompt.strip() == "":
        return

    username = message.author.id
    model = replicate.models.get("stability-ai/stable-diffusion")
    version = model.versions.get(
        "436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b")

    # https://replicate.com/stability-ai/stable-diffusion/versions/f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1#input
    inputs = {
        'width': 768,
        'height': 768,
        'prompt_strength': 0.8,
        'num_outputs': 1,
        'num_inference_steps': 50,
        'guidance_scale': 7.5,
        'scheduler': "DPMSolverMultistep",
    }
    inputs['prompt'] = prompt
    wait_m = await message.channel.send(messages.message["/wait"])
    prediction = replicate.predictions.create(version=version, input=inputs)
    tm = 40
    output = []
    old_percent_m = ""
    while tm > 0:
        prediction.reload()

        if prediction.status == "failed":
            break
        percent = prediction.logs.split("\n")[-1].split("|")[0]
        percent_m = ""
        if percent:
            percent_m = percent
        if percent_m != old_percent_m:
            # await wait_m.edit_text("Processing request from @" + origin_username + " | " + prompt + " | " + percent_m)
            pass
        old_percent_m = percent_m
        if prediction.status == 'succeeded':
            output = prediction.output
            break
        await asyncio.sleep(5)
        tm -= 5

    if len(output) == 0:
        # await wait_m.edit_text("Try running it again, or try a different prompt")
        return
    generated_image_url = output[0]
    urllib.request.urlretrieve(generated_image_url, f"images/{username}.png")
    photo = open(f"images/{username}.png", "rb")
    await wait_m.delete()
    embed = discord.Embed(title=f"{prompt}\nAn Image Generated by @{message.author}\n\n", color=9699539)
    embed.set_author(
        name=f"{message.author}",
    )
    file = discord.File(photo, 'image.jpg')
    embed.set_image (url=f"attachment://images/{username}.png")
    embed.set_thumbnail(url=f"attachment://images/{username}.png")
    await message.channel.send(file=file, embed=embed)

client.run('MTA3OTY1MDkyNDA5NzcyMDM0Mg.GhBdjz.b1NTpAFtydJx5MCtO8c1h1Exp7JbHXpj2rOEts')