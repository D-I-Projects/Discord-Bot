import discord
from discord.ext import commands
from discord import Intents, Status, Activity, ActivityType, app_commands
from discord.ui import Modal, TextInput, View, Button, Select
import os
import requests
import datetime
import pytz
import uuid
from datetime import date

TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True
intents.bans = True

def is_admin(user_id):
    admin_file = os.path.join(os.path.dirname(__file__), "admin.txt")
    if not os.path.exists(admin_file):
        with open(admin_file, "w") as file:
            file.write("")
        print("admin.txt Datei wurde erstellt.")
        return False
    
    with open(admin_file, "r") as file:
        admin_ids = [int(line.strip()) for line in file.readlines()]
    return user_id in admin_ids
        
timezone_mapping = {
    "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Berlin": "Europe/Berlin",
    "Sydney": "Australia/Sydney",
    "Paris": "Europe/Paris",
    "UTC": "UTC",
    "Japan": "Asia/Tokyo",
    "Germany": "Europe/Berlin",
    "USA": "America/New_York",
    "Chicago": "America/Chicago",
    "Toronto": "America/Toronto",
    "Mexico City": "America/Mexico_City",
    "São Paulo": "America/Sao_Paulo",
    "Moscow": "Europe/Moscow",
    "Dubai": "Asia/Dubai",
    "Hong Kong": "Asia/Hong_Kong",
    "Singapore": "Asia/Singapore",
    "Mumbai": "Asia/Kolkata",
    "Johannesburg": "Africa/Johannesburg",
    "Cairo": "Africa/Cairo",
    "Stockholm": "Europe/Stockholm",
    "Madrid": "Europe/Madrid",
}  # AI generated

start_time = datetime.datetime.now()

file_storage_dir = "saved_files"
os.makedirs(file_storage_dir, exist_ok=True)

text_files = {}

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents=Intents().all())

    async def on_ready(self):
        print("Logged in as " + self.user.name)
        synced = await self.tree.sync()
        print("Slash CMDs Synced " + str(len(synced)) + " Commands")
        
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name='D&I Projects',
        details='Currently working on some exciting projects!',
        state='In the middle of a big update...',
        start=datetime.datetime.now(),
        large_image="icon",
    )
        
    async def on_member_join(self, member):
        channel_id = 1230939254205448242
        channel = self.get_channel(channel_id)
        if channel:
            await channel.send(f'**Welcome**, {member.mention}, to **D&I Projects**!')

client = Client()

class FeedbackModal(Modal):
    def __init__(self):
        super().__init__(title="Feedback")
        
        self.add_item(TextInput(label="Program", style=discord.TextStyle.short))
        self.add_item(TextInput(label="Rate your chosen Program", placeholder="Rate your experience from 1-10"))
        self.add_item(TextInput(label="Why?", placeholder="Why did you give this rating?", style=discord.TextStyle.short))
        self.add_item(TextInput(label="Feature Request", placeholder="What features would you like to see?", style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        program = self.children[0].value
        rating = self.children[1].value
        reason = self.children[2].value
        feature_request = self.children[3].value

        feedback_directory = "feedback"
        
        if not os.path.exists(feedback_directory):
            os.makedirs(feedback_directory)

        files = os.listdir(feedback_directory)
        numbers = []

        for file in files:
            if file.endswith(".txt"):
                filename_without_extension = os.path.splitext(file)[0]
                if filename_without_extension.isdigit():
                    numbers.append(int(filename_without_extension))

        try:
            if not numbers:
                feedback_number = 0
            else:
                feedback_number = max(numbers) + 1
        except ValueError:
            feedback_number = 0

        file_path = os.path.join(feedback_directory, f'{feedback_number}.txt')
        
        response_message = (
            '# Feedback\n\n'
            f'Program : {program}.\n'
            f'Given rating: {rating}.\n'
            f'Reason: {reason}\n'
            f'Feature request: {feature_request}\n\n'
            f'Feedback **#{feedback_number}** has been submitted.'
        )
        
        today_date = date.today().isoformat()
        user_id = interaction.user.id
        
        text_message = (
            '# Feedback\n\n'
            f'Program : {program}'
            f'Submitted by USER-ID : {user_id}\n'
            f'Submitted at: {today_date}\n'
            f'Given rating: {rating}.\n'
            f'Reason: {reason}\n'
            f'Feature request: {feature_request}\n\n'
            f'Feedback Number: **#{feedback_number}**.\n'
            f'Status: None.'
        )
        
        try:
            with open(file_path, "w") as file:
                file.write(text_message)
        except IOError as e:
            await interaction.response.send_message(f"An error occurred while saving feedback: {e}", ephemeral=True)
            return
        
        await interaction.response.send_message(response_message, ephemeral=True)

@app_commands.command(name='feedback', description="Give feedback for our Bot.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def feedback(interaction: discord.Interaction):
    modal = FeedbackModal()
    await interaction.response.send_modal(modal)

class HelpView(View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="D&I Bot", description="Pick this if you need help with our Discord Bot!"),
            discord.SelectOption(label="diec", description="Pick this if you need help with our PyPi Package *diec*!"),
            discord.SelectOption(label="Destor", description="Pick this if you need help with our Program Destor!"),
            discord.SelectOption(label="DiscordBotManager", description="Pick this if you need help with our Program DiscordBotManager!"),
        ]
        super().__init__(placeholder="Choose your software!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_help = self.values[0]
        if selected_help == "D&I Bot":
            await interaction.response.send_message(f"Here you can read the Wiki of our [Discord Bot](https://github.com/D-I-Projects/Discord-Bot/wiki)!", ephemeral=True)
        elif selected_help == "diec":
            await interaction.response.send_message(f"Here you can read the Wiki of our PyPi Package [diec](https://github.com/D-I-Projects/diec)!", ephemeral=True)
        elif selected_help == "Destor":
            await interaction.response.send_message(f"Here you can read the Wiki of our Program [Destor](https://github.com/D-I-Projects/destor)!", ephemeral=True)
        elif selected_help == "DiscordBotManager":
            await interaction.response.send_message(f"Here you can read the Wiki of our Program [DiscordBotManager](https://github.com/D-I-Projects/diec/wiki)!", ephemeral=True)

@app_commands.command(name="help", description="A command that helps you!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Select the software with that you need help with.", view=HelpView(), ephemeral=True)

@app_commands.command(name="ping", description="Show you the current Ping of the Bot!")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Pong! {round(client.latency * 1000)}ms**", ephemeral=True)

class ImportantView(View):
    def __init__(self):
        super().__init__()
        self.add_item(ImportantSelect())

class ImportantSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Terms of Service", description="Sends a link to the Terms of Service Page."),
            discord.SelectOption(label="Privacy Policy", description="Sends a link to the Privacy Policy Page."),
            discord.SelectOption(label="GitHub", description="Sends a link to the GitHub Page of the Bot."),
            discord.SelectOption(label="Discord", description="Sends a link to our Discord Server."),
            discord.SelectOption(label="Version", description="Sends Info about the current version of the Bot for feedback and stuff."),
        ]
        super().__init__(placeholder="Choose the Information you are Interested in!", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_important = self.values[0]
        if selected_important == "Terms of Service":
            await interaction.response.send_message(f"Here you can take a look at our [Terms of Service](https://github.com/D-I-Projects/Discord-Bot/blob/main/terms_of_service.md)!", ephemeral=True)
        elif selected_important == "Privacy Policy":
            await interaction.response.send_message(f"Here you can take a look at our [Privacy Policy](https://github.com/D-I-Projects/Discord-Bot/blob/main/privacy_policy.md)!", ephemeral=True)
        elif selected_important == "GitHub":
            await interaction.response.send_message(f"You can finde the Source Code and stuff under our [GitHub Page](https://github.com/D-I-Projects/Discord-Bot)!", ephemeral=True)
        elif selected_important == "Discord":
            await interaction.response.send_message(f"**A link to our [Discord Server](https://discord.gg/5NDYmBVdSA)**!", ephemeral=True)
        elif selected_important == "Version":
            await interaction.response.send_message(f"**Current version : [v24.8.21](https://github.com/D-I-Projects/Discord-Bot/releases/tag/v24.8.21)**", ephemeral=True)

@app_commands.command(name="important", description="Important Links for the Discord Bot.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def important(interaction: discord.Interaction):
    await interaction.response.send_message("Select the Informations you need here.", view=ImportantView(), ephemeral=True)

@app_commands.command(name="time", description="Shows the current time in the specified timezone.")
async def time_command(interaction: discord.Interaction, location: str):
    try:
        timezone = timezone_mapping.get(location, None)
        if timezone:
            tz = pytz.timezone(timezone)
            current_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            await interaction.response.send_message(f"The current time in **{location}** ({timezone}) is **{current_time}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Unknown location: **{location}**. Please provide a valid city, country, or timezone.", ephemeral=True)
    except pytz.UnknownTimeZoneError:
        await interaction.response.send_message(f"Unknown timezone for location: **{location}**. Please provide a valid city, country, or timezone.", ephemeral=True)

@time_command.autocomplete('location')
async def location_autocomplete(interaction: discord.Interaction, current: str) -> list:
    locations = list(timezone_mapping.keys())
    return [
        app_commands.Choice(name=loc, value=loc)
        for loc in locations if current.lower() in loc.lower()
    ]

@app_commands.command(name="uptime", description="Shows the bot's uptime.")
async def uptime_command(interaction: discord.Interaction):
    current_time = datetime.datetime.now()
    uptime_duration = current_time - start_time
    uptime_days = uptime_duration.days
    uptime_seconds = uptime_duration.seconds
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_message = f"Uptime: {uptime_days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    await interaction.response.send_message(uptime_message, ephemeral=True)

@app_commands.command(name="savefile", description="Saves a text file.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def save_file_command(interaction: discord.Interaction, file_name: str, content: str):
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(file_storage_dir, f"{unique_id}.txt")
    with open(file_path, 'w') as file:
        file.write(content)
    text_files[unique_id] = {'file_name': file_name, 'file_path': file_path}
    await interaction.response.send_message(f"File **{file_name}** saved with ID **{unique_id}**.", ephemeral=True)

@app_commands.command(name="getfile", description="Retrieves a saved text file.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_file_command(interaction: discord.Interaction, file_id: str):
    file_data = text_files.get(file_id, None)
    if file_data:
        file_path = file_data['file_path']
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
            await interaction.response.send_message(f"File **{file_data['file_name']}** content:\n\n{file_content}\n", ephemeral=True)
        else:
            await interaction.response.send_message(f"File **{file_data['file_name']}** is no longer available.", ephemeral=True)
    else:
        await interaction.response.send_message(f"No file found with ID **{file_id}**.", ephemeral=True)
        
@app_commands.command(name="deletefile", description="Deletes a saved text file.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def delete_file_command(interaction: discord.Interaction, file_id: str):
    file_data = text_files.get(file_id, None)
    if file_data:
        file_path = file_data['file_path']
        if os.path.exists(file_path):
            os.remove(file_path)
            del text_files[file_id]
            await interaction.response.send_message(f"File **{file_data['file_name']}** deleted successfully.", ephemeral=True)
        else:
            await interaction.response.send_message(f"File **{file_data['file_name']}** is already deleted.", ephemeral=True)
    else:
        await interaction.response.send_message(f"No file found with ID **{file_id}**.", ephemeral=True)

client.tree.add_command(help_command)
client.tree.add_command(ping)
client.tree.add_command(important)
client.tree.add_command(time_command)
client.tree.add_command(uptime_command)
client.tree.add_command(save_file_command)
client.tree.add_command(get_file_command)
client.tree.add_command(delete_file_command)
client.tree.add_command(feedback)

client.run(TOKEN)
