import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image
import tempfile
import os
import uuid
TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

# スラッシュコマンド同期
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"同期完了: {len(synced)}個")
    except Exception as e:
        print(e)

    print(f"ログイン: {bot.user}")


@bot.tree.command(name="gif", description="画像をGIF化します")
@app_commands.describe(
    image="jpg/png画像",
    effect="エフェクト"
)
@app_commands.choices(effect=[
    app_commands.Choice(name="blink", value="blink"),
    app_commands.Choice(name="spin", value="spin"),
    app_commands.Choice(name="zoom", value="zoom")
])
async def gif_command(
    interaction: discord.Interaction,
    image: discord.Attachment,
    effect: app_commands.Choice[str]
):

    await interaction.response.defer()

    # 一時ファイル名
    uid = str(uuid.uuid4())

    input_path = os.path.join(tempfile.gettempdir(), f"{uid}_input")
    output_path = os.path.join(tempfile.gettempdir(), f"{uid}_output.gif")

    try:
        # 画像保存
        await image.save(input_path)

        # Pillowで読み込み
        img = Image.open(input_path).convert("RGBA")

        frames = []

        # ===== エフェクト =====

        if effect.value == "blink":

            for i in range(10):
                if i % 2 == 0:
                    frame = img.copy()
                else:
                    frame = Image.new("RGBA", img.size, (255, 255, 255, 0))

                frames.append(frame)

        elif effect.value == "spin":

            for angle in range(0, 360, 20):
                frame = img.rotate(angle, expand=True)
                frames.append(frame)

        elif effect.value == "zoom":

            width, height = img.size

            for scale in range(100, 150, 5):

                new_w = int(width * scale / 100)
                new_h = int(height * scale / 100)

                resized = img.resize((new_w, new_h))

                canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

                x = (width - new_w) // 2
                y = (height - new_h) // 2

                canvas.paste(resized, (x, y), resized)

                frames.append(canvas)

        # GIF保存
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=80,
            loop=0,
            disposal=2
        )

        await interaction.followup.send(
            file=discord.File(output_path)
        )

    except Exception as e:
        await interaction.followup.send(
            f"エラー: {e}"
        )

    finally:
        # 後始末
        try:
            os.remove(input_path)
        except:
            pass

        try:
            os.remove(output_path)
        except:
            pass


bot.run(TOKEN)
