import discord
from discord.ext import commands, tasks
from discord import Intents, Status, Activity, ActivityType, app_commands
import pystray
from PIL import ImageDraw, Image
import threading
import os
import requests
import datetime
import pytz
import uuid
import random
import sys

intents = discord.Intents.default()
intents.message_content = True
intents.bans = True

def load_image(size=(500, 500)):
    image = Image.new('RGB', size, (255, 255, 255))
    
    dc = ImageDraw.Draw(image)
    
    dc.rectangle((0, 0, size[0], size[1]), fill=(54, 57, 63))
    
    inner_size = (int(size[0] * 0.8), int(size[1] * 0.8))
    inner_pos = ((size[0] - inner_size[0]) // 2, (size[1] - inner_size[1]) // 2)
    dc.rectangle((inner_pos[0], inner_pos[1], inner_pos[0] + inner_size[0], inner_pos[1] + inner_size[1]), fill=(255, 255, 255))
    
    dc.line([(inner_pos[0] + inner_size[0] * 0.2, inner_pos[1]), (inner_pos[0] + inner_size[0], inner_pos[1] + inner_size[1] * 0.4)], fill=(255, 255, 255), width=6)
    dc.line([(inner_pos[0] + inner_size[0] * 0.2, inner_pos[1] + inner_size[1]), (inner_pos[0] + inner_size[0], inner_pos[1] + inner_size[1] * 0.6)], fill=(255, 255, 255), width=6)
    dc.line([(inner_pos[0], inner_pos[1] + inner_size[1] * 0.5), (inner_pos[0] + inner_size[0] * 0.2, inner_pos[1] + inner_size[1] * 0.5)], fill=(255, 255, 255), width=6)
    dc.line([(inner_pos[0] + inner_size[0] * 0.8, inner_pos[1] + inner_size[1] * 0.5), (inner_pos[0] + inner_size[0], inner_pos[1] + inner_size[1] * 0.5)], fill=(255, 255, 255), width=6)
    
    return image

def create_tray_icon():
    """
    Creates the tray icon.
    """
    icon = pystray.Icon("test_icon")
    icon.icon = load_image()
    icon.title = "D&I Bot"

    exit_action = pystray.MenuItem("Exit", exit_application)
    icon.menu = pystray.Menu(exit_action)

    icon.run()

def start_tray_icon():
    """
    Starts the tray icon in a separate thread.
    """
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

def exit_application(icon):
    icon.stop()
    sys.exit(0)

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
}

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

    async def send_private_message(self, user_id, content):
        user = await self.fetch_user(user_id)
        if user:
            try:
                await user.send(content)
            except discord.HTTPException as e:
                print(f"Failed to send DM to user {user_id}: {e}")
        else:
            print(f"User with ID {user_id} not found.")
            
    async def on_member_join(self, member):
        channel_id = 1230939254205448242
        channel = self.get_channel(channel_id)
        if channel:
            await channel.send(f'**Welcome**, {member.mention}, to **D&I Projects**!')

TOKEN = "No way."

client = Client()

def get_latest_release(repo_url):
    response = requests.get(f'https://api.github.com/repos/{repo_url}/releases/latest')
    if response.status_code == 200:
        release_data = response.json()
        return release_data['tag_name'], release_data['html_url']
    return "Unknown", None

@app_commands.command(name="help", description="A command that helps you!")
async def help_command(interaction: discord.Interaction, types_help: str):
    if types_help == "D&I Bot":
        help_link = "https://github.com/wfxey/Discord-Bot/wiki"
    elif types_help == "Destor":
        help_link = "https://github.com/wfxey/Destor/wiki"
    elif types_help == "PC Info":
        help_link = "https://github.com/wfxey/PC-Info/wiki"
    elif types_help == "DiscordBotCreator":
        help_link = "https://github.com/wfxey/DiscordBotCreator/wiki"
    else:
        help_link = "Unknown"
    
    await interaction.response.send_message(f'Read our documentation about **{types_help}** at **{help_link}**!')

@help_command.autocomplete('types_help')
async def type_help_autocomplete(interaction: discord.Interaction, current: str) -> list:
    types_help = ['D&I Bot', 'Destor', 'DiscordBotCreator', 'PC Info']
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

@app_commands.command(name="discord", description="Sends a Discord Server Link for our Server!")
async def discord_command(interaction: discord.Interaction):
    await interaction.response.send_message('**Our Discord Server**: **https://discord.gg/NJUkdptb9S**')

@app_commands.command(name="release", description="Shows you the newest version of the program!")
async def release_command(interaction: discord.Interaction, types_release: str):
    repo_map = {
        "D&I Center": "wfxey/D-I-Bot",
        "Destor": "wfxey/Destor",
        "PC Info": "wfxey/PC-Info",
        "DiscordBotCreator": "wfxey/DiscordBotCreator",
        "Keylogger": "wfxey/Keylogger"
    }
    
    repo_url = repo_map.get(types_release, None)
    
    if repo_url:
        tag_name, release_link = get_latest_release(repo_url)
        await interaction.response.send_message(f'The newest version of **{types_release}** is **{tag_name}**. Read more at **{release_link}**!')
    else:
        await interaction.response.send_message(f'Read our documentation about **{types_release}** at **Unknown**!')

@app_commands.command(name="send_message_as_user", description="Sendet eine Nachricht im Namen eines anderen Benutzers.")
async def send_message_as_user(interaction: discord.Interaction, member: discord.Member, message: str):
    user_id = interaction.user.id
    if not is_admin(user_id):
        await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl zu verwenden.", ephemeral=True)
        return
    
    await interaction.response.defer()
    try:
        await member.send(message)
        await interaction.followup.send("Nachricht wurde gesendet.")
    except discord.Forbidden:
        await interaction.followup.send("Ich kann dem Benutzer keine Nachricht senden.")

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

@release_command.autocomplete('types_release')
async def type_release_autocomplete(interaction: discord.Interaction, current: str) -> list:
    types_release = ['D&I Center', 'Destor', 'DiscordBotCreator', 'PC Info', 'Keylogger']
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
            await interaction.response.send_message(f"File **{file_data['file_name']}** content:\n```\n{file_content}\n```")
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

@app_commands.command(name="announce", description="Sendet eine Ankündigung an einen bestimmten Kanal.")
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
    
@app_commands.command(name="format_code", description="Formats a given code snippet.")
async def format_code(interaction: discord.Interaction, language: str, code: str):
    formatted_code = f"```{language}\n{code}\n```"
    await interaction.response.send_message(f"Here is your formatted code:\n{formatted_code}")

@app_commands.command(name="hex_to_rgb", description="Converts a hex color code to RGB values.")
async def hex_to_rgb(interaction: discord.Interaction, hex_code: str):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) != 6:
        await interaction.response.send_message("Invalid hex code. Please provide a valid 6-character hex code.")
        return
    rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    await interaction.response.send_message(f"The RGB value for `{hex_code}` is `{rgb}`")

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

def read_gui_program_ideas():
    with open('gui_program_ideas.txt', 'r', encoding='utf-8') as file:
        ideas = [line.strip() for line in file.readlines()]
    return ideas

gui_program_ideas = read_gui_program_ideas()

@app_commands.command(name="gui_challenge", description="Fetches a daily coding challenge or GUI program idea.")
async def gui_challenge(interaction: discord.Interaction):
    try:
        daily_challenges = [
    {
        "title": "Personal Finance Tracker",
        "description": "A desktop application for tracking personal finances, including income, expenses, savings goals, and budgeting."
    },
    {
        "title": "Task Manager",
        "description": "A GUI application to manage tasks, including adding, editing, marking as complete, and deleting tasks."
    },
    {
        "title": "Weather App",
        "description": "An application that displays current weather conditions and forecasts for user-specified locations."
    },
    {
        "title": "Recipe Book",
        "description": "A digital cookbook where users can store and organize recipes, search by ingredients or categories, and create meal plans."
    },
    {
        "title": "Note-taking Application",
        "description": "A tool for creating, editing, and organizing notes with support for text formatting and categorization."
    },
    {
        "title": "Image Viewer and Editor",
        "description": "An application for viewing images and performing basic editing tasks such as cropping, resizing, and applying filters."
    },
    {
        "title": "Music Player",
        "description": "A GUI-based music player that allows users to play, pause, skip tracks, create playlists, and manage their music library."
    },
    {
        "title": "Chat Application",
        "description": "A real-time messaging application with support for one-on-one and group chats, message history, and multimedia sharing."
    },
    {
        "title": "Calendar Scheduler",
        "description": "A GUI calendar application for scheduling events, setting reminders, and managing daily, weekly, and monthly tasks."
    },
    {
        "title": "To-Do List",
        "description": "A simple to-do list manager with features for adding tasks, marking them as completed, and organizing by priority."
    },
    {
        "title": "Video Player",
        "description": "A multimedia player that supports playback of video files with features for playback control, subtitles, and playlists."
    },
    {
        "title": "E-book Reader",
        "description": "An application for reading e-books with features for bookmarking, highlighting, and adjusting text settings."
    },
    {
        "title": "Expense Tracker",
        "description": "An application for tracking expenses, categorizing spending, setting budgets, and generating financial reports."
    },
    {
        "title": "Drawing Program",
        "description": "A graphical tool for creating digital drawings and sketches with options for different brushes, colors, and layers."
    },
    {
        "title": "Fitness Tracker",
        "description": "A GUI-based fitness app for tracking workouts, setting fitness goals, and monitoring progress over time."
    },
    {
        "title": "Password Manager",
        "description": "An application for securely storing and managing passwords, with features for generating strong passwords and encryption."
    },
    {
        "title": "File Explorer",
        "description": "A GUI-based file manager with functionalities for browsing files, organizing directories, and performing file operations."
    },
    {
        "title": "Social Media Dashboard",
        "description": "An interface for managing multiple social media accounts, scheduling posts, and analyzing engagement metrics."
    },
    {
        "title": "Language Learning App",
        "description": "An interactive application for learning languages with vocabulary quizzes, grammar lessons, and pronunciation practice."
    },
    {
        "title": "Virtual Assistant",
        "description": "A GUI interface for a virtual assistant that can answer questions, perform tasks, and provide information based on user input."
    },
    {
        "title": "Photo Album Organizer",
        "description": "An application for organizing digital photo albums with features for tagging, sorting by date/location, and creating slideshows."
    },
    {
        "title": "Job Search Tracker",
        "description": "A GUI tool for organizing job applications, tracking application statuses, and managing interview schedules."
    },
    {
        "title": "Home Automation Control Panel",
        "description": "An interface for controlling smart home devices, adjusting settings, and scheduling automation routines."
    },
    {
        "title": "Code Snippet Manager",
        "description": "A tool for storing and categorizing code snippets, with syntax highlighting, search capabilities, and export options."
    },
    {
        "title": "Project Management Tool",
        "description": "A GUI-based application for managing projects, assigning tasks, tracking progress, and collaborating with team members."
    },
    {
        "title": "Video Conferencing App",
        "description": "A GUI application for conducting video conferences with features for screen sharing, chat, and recording meetings."
    },
    {
        "title": "Virtual Tour Guide",
        "description": "An interactive application for exploring virtual tours of landmarks, museums, and travel destinations."
    },
    {
        "title": "Budget Planner",
        "description": "A financial planning tool with budget tracking, expense categorization, savings goal setting, and financial forecasting."
    },
    {
        "title": "Health Tracker",
        "description": "An application for monitoring health metrics such as weight, exercise activity, calorie intake, and sleep patterns."
    },
    {
        "title": "Dashboard for IoT Devices",
        "description": "An interface for monitoring and controlling Internet of Things (IoT) devices, sensors, and home automation systems."
    },
    {
        "title": "Podcast Player",
        "description": "A GUI-based player for streaming and downloading podcasts, with features for subscribing, episode management, and playback."
    },
    {
        "title": "Language Translator",
        "description": "An application for translating text and speech between different languages, with support for multiple translation services."
    },
    {
        "title": "Video Editing Software",
        "description": "A GUI-based tool for editing videos, including cutting, merging, adding effects, captions, and exporting in various formats."
    },
    {
        "title": "Inventory Management System",
        "description": "An application for managing inventory levels, tracking stock movements, generating reports, and setting alerts."
    },
    {
        "title": "Cinema Booking System",
        "description": "A GUI interface for booking movie tickets, selecting seats, viewing showtimes, and processing payments."
    },
    {
        "title": "Music Production Studio",
        "description": "A graphical interface for composing, arranging, and mixing music tracks with virtual instruments and effects."
    },
    {
        "title": "Virtual Classroom",
        "description": "An online learning platform with features for live lectures, interactive quizzes, assignments, and student progress tracking."
    },
    {
        "title": "Weather Dashboard",
        "description": "An interactive dashboard displaying weather forecasts, radar maps, and weather alerts for selected locations."
    },
    {
        "title": "Document Scanner",
        "description": "A GUI application for scanning and digitizing documents using a webcam or flatbed scanner, with OCR capabilities."
    },
    {
        "title": "E-commerce Storefront",
        "description": "A graphical interface for managing an online store, including product listings, shopping cart, checkout process, and order management."
    },
    {
        "title": "Online Voting System",
        "description": "A secure GUI-based platform for conducting elections and polls, with voter authentication and result tabulation."
    },
    {
        "title": "Art Gallery Exhibition Viewer",
        "description": "A virtual exhibition space showcasing artwork, sculptures, and multimedia installations with interactive features."
    },
    {
        "title": "Cryptocurrency Portfolio Tracker",
        "description": "An application for managing investments in cryptocurrencies, tracking portfolio performance, and analyzing market trends."
    },
    {
        "title": "Pet Care Scheduler",
        "description": "A GUI tool for managing pet care routines, including feeding schedules, vet appointments, and medication reminders."
    },
    {
        "title": "Math Tutoring App",
        "description": "An interactive application for learning and practicing math concepts with tutorials, quizzes, and progress tracking."
    },
    {
        "title": "Cooking Recipe Generator",
        "description": "A GUI tool that generates recipes based on selected ingredients, dietary preferences, and cooking methods."
    },
    {
        "title": "Language Pronunciation Trainer",
        "description": "An interactive tool for improving pronunciation in foreign languages through audio exercises and feedback."
    },
    {
        "title": "Family Tree Builder",
        "description": "A graphical application for creating and visualizing family trees, adding photos, dates, and historical information."
    },
    {
        "title": "Virtual Pet Game",
        "description": "An interactive game where users can adopt and care for virtual pets, including feeding, grooming, and playing activities."
    },
    {
        "title": "Job Interview Preparation Tool",
        "description": "A GUI-based application for practicing job interview scenarios, answering questions, and receiving feedback."
    },
    {
        "title": "Digital Art Gallery",
        "description": "A virtual gallery showcasing digital artworks with options for virtual tours, artist profiles, and interactive exhibits."
    },
    {
        "title": "Home Workout Planner",
        "description": "An application for planning and tracking home workout routines, including exercises, sets, and progress charts."
    },
    {
        "title": "Virtual Piano",
        "description": "A GUI-based piano application that allows users to play music using a virtual keyboard with different instrument sounds."
    },
    {
        "title": "Study Planner",
        "description": "A tool for organizing study schedules, setting study goals, tracking study hours, and managing academic."
    }
    ]
        
        challenge = random.choice(daily_challenges)
            
        challenge_title = challenge["title"]
        challenge_description = challenge["description"]
            
        await interaction.response.send_message(f"**Daily GUI Challenge:**\n**Title:** {challenge_title}\n**Description:** {challenge_description}")
    
    except Exception as e:
        await interaction.response.send_message(f"Error fetching daily challenge: {str(e)}")
        
client.tree.add_command(help_command)
client.tree.add_command(ping)
client.tree.add_command(format_code)
client.tree.add_command(discord_command)
client.tree.add_command(release_command)
client.tree.add_command(time_command)
client.tree.add_command(uptime_command)
client.tree.add_command(save_file_command)
client.tree.add_command(get_file_command)
client.tree.add_command(delete_file_command)
client.tree.add_command(hex_to_rgb)
client.tree.add_command(github_repo_info)
client.tree.add_command(pypi_command)
client.tree.add_command(gui_challenge)
client.tree.add_command(announce)
client.tree.add_command(send_message_as_user)

start_tray_icon()

client.run(TOKEN)