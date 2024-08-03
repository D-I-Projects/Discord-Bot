import discord
from discord.ext import commands
from discord import Intents, Status, Activity, ActivityType, app_commands
from discord.ui import Modal, TextInput, View, Button
import os
import requests
import datetime
import pytz
import uuid
from datetime import date

STATUS_CHANNEL_ID = 1263951082187526225

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
    "SÃ£o Paulo": "America/Sao_Paulo",
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
        
        activity = Activity(
            type=ActivityType.playing,
            name='Destor',
            application_id=1245459087584661513,
        )
        
        await self.change_presence(status=Status.online, activity=activity)


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
            f'Program : {program}.\n'
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
async def feedback(interaction: discord.Interaction):
    modal = FeedbackModal()
    await interaction.response.send_modal(modal)

def get_latest_release(repo_url):
    response = requests.get(f'https://api.github.com/repos/{repo_url}/releases/latest')
    if response.status_code == 200:
        release_data = response.json()
        return release_data['tag_name'], release_data['html_url']
    return "Unknown", None

@app_commands.command(name="help", description="A command that helps you!")
async def help_command(interaction: discord.Interaction, types_help: str):
    if types_help == "D&I Bot":
        help_link = "https://d-i-projects.github.io/project/discord-bot/"
    elif types_help == "diec":
        help_link = "https://d-i-projects.github.io/project/diec/"
    elif types_help == "Destor":
        help_link = "https://d-i-projects.github.io/project/destor/"
    elif types_help == "DiscordBotManager":
        help_link = "https://d-i-projects.github.io/project/discordbotmanager/"
    else:
        help_link = "Unknown"
    
    await interaction.response.send_message(f'Read our documentation about **{types_help}** at **{help_link}**!')

@help_command.autocomplete('types_help')
async def type_help_autocomplete(interaction: discord.Interaction, current: str) -> list:
    types_help = ['diec', 'D&I Bot', 'Destor', 'DiscordBotManager']
    return [
        app_commands.Choice(name=help_type, value=help_type)
        for help_type in types_help if current.lower() in help_type.lower()
    ]

@app_commands.command(name="ping", description="Show you the current Ping of the Bot!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Pong! {round(client.latency * 1000)}ms**")
    
@app_commands.command(name="privacy", description="Information about the privacy of text files.")
async def privacy(interaction: discord.Interaction):
    await interaction.response.send_message(
        "All text files you save are not private. We will even check them to ensure no one is bypassing rules. You can use the function, but do NOT share any sensitive data!"
    )

@app_commands.command(name="discord", description="Sends a valid Discord Server Link for our Server!")
async def discord_command(interaction: discord.Interaction):
    await interaction.response.send_message('**Our Discord Server**: **https://discord.gg/5NDYmBVdSA**')

@app_commands.command(name="release", description="Shows you the newest version of the program!")
async def release_command(interaction: discord.Interaction, types_release: str):
    repo_map = {
        "D&I Bot": "D-I-Projects/Discord-Bot",
        "Destor": "D-I-Projects/Destor",
        "DiscordBotManager": "D-I-Projects/DiscordBotManager",
        "d-i-projects.github.io" : "D-I-Projects/d-i-projects.github.io",
        "diec" : "D-I-Projects/diec",
        "diec-test-gui" : "D-I-Projects/diec-test-gui",
    }
    
    repo_url = repo_map.get(types_release, None)
    
    if repo_url:
        tag_name, release_link = get_latest_release(repo_url)
        await interaction.response.send_message(f'The newest version of **{types_release}** is **{tag_name}**. Read more at **{release_link}**!')
    else:
        await interaction.response.send_message(f'Read our documentation about **{types_release}** at **Unknown**!')

@app_commands.command(name="website", description="Sends a link Website")
async def website_command(interaction: discord.Interaction):
    await interaction.response.send_message("**Our Website for Documentations and more is** : https://d-i-projects.github.io/")

@release_command.autocomplete('types_release')
async def type_release_autocomplete(interaction: discord.Interaction, current: str) -> list:
    types_release = ['D&I Bot', 'Destor', 'DiscordBotManager', 'd-i-projects.github.io', 'diec', 'diec-test-gui']
    return [
        app_commands.Choice(name=release_type, value=release_type)
        for release_type in types_release if current.lower() in release_type.lower()
    ]

@app_commands.command(name="time", description="Shows the current time in the specified timezone.")
async def time_command(interaction: discord.Interaction, location: str):
    try:
        timezone = timezone_mapping.get(location, None)
        if timezone:
            tz = pytz.timezone(timezone)
            current_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            await interaction.response.send_message(f"The current time in **{location}** ({timezone}) is **{current_time}**.")
        else:
            await interaction.response.send_message(f"Unknown location: **{location}**. Please provide a valid city, country, or timezone.")
    except pytz.UnknownTimeZoneError:
        await interaction.response.send_message(f"Unknown timezone for location: **{location}**. Please provide a valid city, country, or timezone.")

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
    await interaction.response.send_message(uptime_message)

@app_commands.command(name="savefile", description="Saves a text file.")
async def save_file_command(interaction: discord.Interaction, file_name: str, content: str):
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(file_storage_dir, f"{unique_id}.txt")
    with open(file_path, 'w') as file:
        file.write(content)
    text_files[unique_id] = {'file_name': file_name, 'file_path': file_path}
    await interaction.user.send(f'File **{file_name}** saved with ID **{unique_id}**.')

@app_commands.command(name="getfile", description="Retrieves a saved text file.")
async def get_file_command(interaction: discord.Interaction, file_id: str):
    file_data = text_files.get(file_id, None)
    if file_data:
        file_path = file_data['file_path']
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
            await interaction.response.send_message(f"File **{file_data['file_name']}** content:\n\n{file_content}\n")
        else:
            await interaction.response.send_message(f"File **{file_data['file_name']}** is no longer available.")
    else:
        await interaction.response.send_message(f"No file found with ID **{file_id}**.")
        
@app_commands.command(name="deletefile", description="Deletes a saved text file.")
async def delete_file_command(interaction: discord.Interaction, file_id: str):
    file_data = text_files.get(file_id, None)
    if file_data:
        file_path = file_data['file_path']
        if os.path.exists(file_path):
            os.remove(file_path)
            del text_files[file_id]
            await interaction.response.send_message(f"File **{file_data['file_name']}** deleted successfully.")
        else:
            await interaction.response.send_message(f"File **{file_data['file_name']}** is already deleted.")
    else:
        await interaction.response.send_message(f"No file found with ID **{file_id}**.")

@app_commands.command(name="announce", description="Sendet eine AnkÃ¼ndigung an einen bestimmten Kanal.")
async def announce(interaction: discord.Interaction, message: str):
    user_id = interaction.user.id
    if not is_admin(user_id):
        await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl zu verwenden.", ephemeral=True)
        return
    
    channel_id = 1230939345553199105
    channel = interaction.client.get_channel(channel_id)
    if channel:
        await channel.send(message)
        await interaction.response.send_message("Nachricht wurde gesendet.", ephemeral=True)
    else:
        await interaction.response.send_message("Kanal nicht gefunden.", ephemeral=True)

@app_commands.command(name="github_repo_info", description="Retrieves information about a GitHub repository.")
async def github_repo_info(interaction: discord.Interaction, repo_url: str):
    try:
        parts = repo_url.strip("/").split("/")
        owner = parts[-2]
        repo_name = parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(api_url, headers=headers)
        repo_data = response.json()

        if response.status_code == 200:
            description = repo_data.get('description', 'No description available')
            stars = repo_data.get('stargazers_count', 'Unknown')
            forks = repo_data.get('forks_count', 'Unknown')
            language = repo_data.get('language', 'Unknown')
            message = (f"**Repository:** {repo_url}\n"
                    f"**Description:** {description}\n"
                    f"**Stars:** {stars}\n"
                    f"**Forks:** {forks}\n"
                    f"**Main Language:** {language}")
        else:
            message = f"Failed to fetch repository information. Status code: {response.status_code}"
        
        await interaction.response.send_message(message)
    
    except Exception as e:
        await interaction.response.send_message(f"Error retrieving GitHub repository information: {str(e)}")
        
@app_commands.command(name="pypi", description="Fetches information about a Python package from PyPI.")
async def pypi_command(interaction: discord.Interaction, package_name: str):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            package_info = response.json()
            latest_version = package_info["info"]["version"]
            summary = package_info["info"]["summary"]
            await interaction.response.send_message(f"**Package:** {package_name}\n**Latest Version:** {latest_version}\n**Summary:** {summary}")
        else:
            await interaction.response.send_message(f"Failed to fetch information for package '{package_name}'.")
    except Exception as e:
        await interaction.response.send_message(f"Error fetching package information: {str(e)}")

client.tree.add_command(help_command)
client.tree.add_command(ping)
client.tree.add_command(discord_command)
client.tree.add_command(release_command)
client.tree.add_command(time_command)
client.tree.add_command(uptime_command)
client.tree.add_command(save_file_command)
client.tree.add_command(get_file_command)
client.tree.add_command(delete_file_command)
client.tree.add_command(github_repo_info)
client.tree.add_command(pypi_command)
client.tree.add_command(announce)
client.tree.add_command(website_command)
client.tree.add_command(feedback)

client.run(TOKEN)
