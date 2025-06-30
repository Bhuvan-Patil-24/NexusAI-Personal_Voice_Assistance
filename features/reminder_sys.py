import sqlite3
import threading
import time
from datetime import datetime
from dateparser import parse
import atexit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReminderSystem:
    def __init__(self, db_path="nexus_ai_data/reminders.db"):
        self.db_path = db_path
        self.active_reminders = {}  # Store active reminder threads
        self.running = True
        self.reminder_callback = None  # Callback function for when reminder triggers
        self.init_db()

        # Register cleanup function
        atexit.register(self.cleanup)

        # Load existing reminders on startup
        self.load_all_reminders()

    def set_reminder_callback(self, callback_function):
        """Set the callback function that will be called when a reminder triggers"""
        self.reminder_callback = callback_function

    def init_db(self):
        """Initialize the database with reminders table"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )''')
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def add_reminder(self, reminder_text, time_str):
        """Add a new reminder"""
        try:
            # Parse the time string
            reminder_time = parse(time_str)
            if not reminder_time:
                return False, "Sorry, I couldn't understand the reminder time. Please try again with a clearer time format."

            # Check if time is in the past
            if reminder_time <= datetime.now():
                return False, "The reminder time is in the past. Please set a future time."

            # Store in database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO reminders (text, time) VALUES (?, ?)",
                      (reminder_text, reminder_time.isoformat()))
            conn.commit()
            reminder_id = c.lastrowid
            conn.close()

            # Schedule the reminder
            self.schedule_reminder(reminder_id, reminder_text, reminder_time)

            formatted_time = reminder_time.strftime(
                '%A, %B %d, %Y at %I:%M %p')
            success_msg = f"Reminder set successfully for {formatted_time}: '{reminder_text}'"
            logger.info(
                f"Reminder {reminder_id} added: {reminder_text} at {reminder_time}")

            return True, success_msg

        except Exception as e:
            logger.error(f"Error adding reminder: {e}")
            return False, "Sorry, there was an error setting your reminder. Please try again."

    def schedule_reminder(self, reminder_id, text, remind_time):
        """Schedule a reminder to trigger at the specified time"""
        def reminder_job():
            try:
                # Wait until the reminder time
                while datetime.now() < remind_time and self.running:
                    time.sleep(1)

                if self.running:
                    # Trigger the reminder
                    reminder_message = f"🔔 Reminder: {text}"

                    # Use callback if available, otherwise just log
                    if self.reminder_callback:
                        self.reminder_callback(reminder_message)
                    else:
                        print(reminder_message)

                    logger.info(f"Reminder {reminder_id} triggered: {text}")

                    # Remove from database after triggering
                    self.remove_reminder(reminder_id)

                    # Remove from active reminders
                    if reminder_id in self.active_reminders:
                        del self.active_reminders[reminder_id]

            except Exception as e:
                logger.error(f"Error in reminder job {reminder_id}: {e}")

        # Start the reminder thread
        reminder_thread = threading.Thread(target=reminder_job, daemon=True)
        reminder_thread.start()

        # Store the thread reference
        self.active_reminders[reminder_id] = {
            'thread': reminder_thread,
            'text': text,
            'time': remind_time
        }

    def remove_reminder(self, reminder_id):
        """Remove a reminder from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            conn.close()
            logger.info(f"Reminder {reminder_id} removed from database")
        except Exception as e:
            logger.error(f"Error removing reminder {reminder_id}: {e}")

    def cancel_reminder(self, reminder_id):
        """Cancel an active reminder"""
        try:
            # Remove from active reminders
            if reminder_id in self.active_reminders:
                del self.active_reminders[reminder_id]

            # Remove from database
            self.remove_reminder(reminder_id)
            return True, f"Reminder {reminder_id} has been cancelled."

        except Exception as e:
            logger.error(f"Error cancelling reminder {reminder_id}: {e}")
            return False, "Error cancelling the reminder."

    def list_reminders(self):
        """List all active reminders"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, text, time FROM reminders ORDER BY time")
            rows = c.fetchall()
            conn.close()

            if not rows:
                return "You have no active reminders."

            reminder_list = "Your active reminders:\n"
            for row in rows:
                reminder_id, text, time_str = row
                remind_time = datetime.fromisoformat(time_str)
                formatted_time = remind_time.strftime(
                    '%A, %B %d, %Y at %I:%M %p')
                reminder_list += f"{reminder_id}. {text} - {formatted_time}\n"

            return reminder_list.strip()

        except Exception as e:
            logger.error(f"Error listing reminders: {e}")
            return "Error retrieving reminders."

    def load_all_reminders(self):
        """Load and schedule all reminders from database on startup"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, text, time FROM reminders")
            rows = c.fetchall()
            conn.close()

            current_time = datetime.now()
            expired_reminders = []

            for row in rows:
                reminder_id, text, time_str = row
                remind_time = datetime.fromisoformat(time_str)

                if remind_time <= current_time:
                    # Reminder time has passed, remove it
                    expired_reminders.append(reminder_id)
                else:
                    # Schedule the reminder
                    self.schedule_reminder(reminder_id, text, remind_time)
                    logger.info(
                        f"Loaded reminder {reminder_id}: {text} at {remind_time}")

            # Clean up expired reminders
            for reminder_id in expired_reminders:
                self.remove_reminder(reminder_id)
                logger.info(f"Removed expired reminder {reminder_id}")

            if rows:
                active_count = len(rows) - len(expired_reminders)
                logger.info(
                    f"Loaded {active_count} active reminders, removed {len(expired_reminders)} expired reminders")

        except Exception as e:
            logger.error(f"Error loading reminders: {e}")

    def process_reminder(self, command_text):
        """Process natural language reminder commands"""
        command_lower = command_text.lower().strip()

        if command_lower.startswith(('set reminder', 'remind me', 'set a reminder')):
            # Extract reminder text and time
            parts = command_text.split(' to ', 1)
            if len(parts) == 2:
                time_and_text = parts[1]
                # Try to find time patterns
                time_parts = time_and_text.split(' that ', 1)
                if len(time_parts) == 2:
                    time_str = time_parts[0].strip()
                    reminder_text = time_parts[1].strip()
                else:
                    # Alternative parsing
                    words = time_and_text.split()
                    # Look for common time indicators
                    time_indicators = ['at', 'on', 'in', 'tomorrow', 'today', 'monday',
                                       'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    time_start = -1
                    for i, word in enumerate(words):
                        if word.lower() in time_indicators or ':' in word or word.isdigit():
                            time_start = i
                            break

                    if time_start != -1:
                        reminder_text = ' '.join(words[:time_start]).strip()
                        time_str = ' '.join(words[time_start:]).strip()
                    else:
                        return False, "Please specify when you want to be reminded."

                if reminder_text and time_str:
                    return self.add_reminder(reminder_text, time_str)
                else:
                    return False, "Please specify both what to remind you about and when."
            else:
                return False, "Please use format like 'remind me to call mom at 3pm' or 'set reminder to meeting tomorrow at 2pm'"

        elif command_lower in ['list reminders', 'show reminders', 'my reminders']:
            return True, self.list_reminders()

        elif command_lower.startswith('cancel reminder'):
            try:
                reminder_id = int(command_lower.split()[-1])
                return self.cancel_reminder(reminder_id)
            except:
                return False, "Please specify the reminder ID to cancel (e.g., 'cancel reminder 1')"

        else:
            return False, "I didn't understand that reminder command. Try 'remind me to [task] at [time]' or 'list reminders'"

    def cleanup(self):
        """Clean up resources when shutting down"""
        logger.info("Shutting down reminder system...")
        self.running = False
