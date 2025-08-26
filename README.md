# AutoBot

Step-by-Step Guide to Starting the Telegram Bot Project on Windows
This guide assumes you are starting from scratch on a Windows machine and that your project directory is C:\Users\User\LionMotorsBot.
If the directory is different, adjust the paths accordingly.
The project involves a Python-based Telegram bot, so we'll install Python, create a virtual environment (venv), install dependencies, set up the .env file, and launch the bot.py file.

Step 1:

Go to python.org/downloads.
Download the latest stable version.
In the installer:
Check the box: "Add python.exe to PATH" (important for command-line access).

Step 2:

Open Command Prompt.
run: cd C:\Users\User\LionMotorsBot
run: python -m venv venv
The venv folder should appear in the directory
run: textvenv\Scripts\activate

Step 3: 

Your prompt should change to (venv) C:\Users\User\LionMotorsBot> indicating it's active.
If you get an error (e.g., execution policy issue), run PowerShell as Administrator and execute:
With the venv active, install required libraries:
run: textpip install python-telegram-bot python-dotenv
set up the .env File: BOT_TOKEN=your_bot_token_here
run: python bot.py

Test the bot: Open Telegram, search for your bot, and send /start to verify it responds.

Additional Tips

Deactivate venv: When done, run deactivate in Command Prompt.
Run Again: Next time, navigate to the directory, activate venv, and run python bot.py.
