import discord
from discord import app_commands
from discord.ext import commands
import io
import contextlib
import textwrap


TOKEN = ''  # Replace with your bot token

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

guild_id = None  # Optionally set your guild/server ID for faster command registration

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=guild_id)) if guild_id else await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="py", description="Execute Python code and return the result.")
@app_commands.describe(code="The Python code to execute.")
async def py(interaction: discord.Interaction, code: str):
    # Remove code block formatting if present
    if code.startswith('```') and code.endswith('```'):
        code = '\n'.join(code.strip('`').split('\n')[1:])
    code = textwrap.dedent(code)
    local_vars = {}
    stdout = io.StringIO()
    led_on = False
    heart_override = False
    try:
        # Check for display.show(Image.HEART) in code
        if 'display.show(Image.HEART)' in code.replace(' ', ''):
            heart_override = True
        with contextlib.redirect_stdout(stdout):
            exec(code, {}, local_vars)
        output = stdout.getvalue()
        if not output:
            output = 'No output.'
        led_on = True
    except Exception as e:
        output = f'Error: {e}'
        led_on = False
    # Discord messages have a 2000 character limit
    if len(output) > 1900:
        output = output[:1900] + '\n...output truncated...'
    # LED emoji: red for on, white for off
    led_emoji = '🔴' if led_on else '⚪'
    heart_led = (
        '⚪🔴⚪🔴⚪\n'
        '🔴🔴🔴🔴🔴\n'
        '🔴🔴🔴🔴🔴\n'
        '⚪🔴🔴🔴⚪\n'
        '⚪⚪🔴⚪⚪'
    )
    embed = discord.Embed(
        title=f"{led_emoji} Python Execution",
        description=heart_led if heart_override else f'```py\n{output}\n```',
        color=0xFF0000 if heart_override or led_on else 0xFFFFFF
    )
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_guild_join(guild):
    # Try to find a general or system channel to send the welcome message
    channel = guild.system_channel
    if channel is None:
        for c in guild.text_channels:
            if 'general' in c.name:
                channel = c
                break
        else:
            channel = guild.text_channels[0] if guild.text_channels else None
    if channel:
        await channel.send("Hello! I'm your Python execution bot. Use `/py` to run Python code and get the output.")

if __name__ == '__main__':
    bot.run(TOKEN)
