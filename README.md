# Weather Report Generator

This project is a Python script that automatically generates a weather report for tomorrow's weather at Georgia Tech and sends it to a Discord channel.

## Features

- Fetches weather data from the Open-Meteo API.
- Generates a human-readable weather report using the Google Generative AI API (or a mock version if the API key is not available).
- Sends the report to a specified Discord channel using a webhook.
- Can be automated to run at a specific time every day using a cron job.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project directory and add the following environment variables:

    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    DISCORD_WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL
    ```

    Replace `YOUR_GEMINI_API_KEY` with your Google Generative AI API key and `YOUR_DISCORD_WEBHOOK_URL` with your Discord webhook URL.

## Usage

To run the script manually, execute the following command in your terminal:

```bash
python3 main.py
```

## Automation (Cron Job)

To automate the script to run every day at 7 PM, you can set up a cron job.

1.  Open your crontab configuration by running the following command in your terminal:
    ```bash
    crontab -e
    ```

2.  Add the following line to your crontab file:
    ```
    0 19 * * * /usr/bin/python3 /path/to/your/project/main.py
    ```

    - `0 19 * * *` specifies that the job should run at 7:00 PM (19:00) every day.
    - Replace `/usr/bin/python3` with the absolute path to your Python 3 interpreter. You can find this by running `which python3`.
    - Replace `/path/to/your/project/main.py` with the absolute path to the `main.py` file in your project directory.

3.  Save and close the crontab file. The cron job is now set up and will run automatically.
