import pyautogui
import os
from datetime import datetime


class UIController:
    def __init__(self):
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Small pause between actions

    def switch_tab(self, direction='next'):
        """Switch browser tabs"""
        try:
            if direction == 'next':
                # Ctrl+Tab for next tab
                pyautogui.hotkey('ctrl', 'tab')
            elif direction == 'previous':
                # Ctrl+Shift+Tab for previous tab
                pyautogui.hotkey('ctrl', 'shift', 'tab')
            return True
        except Exception as e:
            print(f"Error switching tab: {e}")
            return False

    def close_tab(self):
        """Close current tab"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            return True
        except Exception as e:
            print(f"Error closing tab: {e}")
            return False

    def close_window(self):
        """Close current window"""
        try:
            pyautogui.hotkey('alt', 'f4')
            return True
        except Exception as e:
            print(f"Error closing window: {e}")
            return False

    def volume_up(self):
        """Increase system volume"""
        try:
            pyautogui.press('volumeup')
            return True
        except Exception as e:
            print(f"Error increasing volume: {e}")
            return False

    def volume_down(self):
        """Decrease system volume"""
        try:
            pyautogui.press('volumedown')
            return True
        except Exception as e:
            print(f"Error decreasing volume: {e}")
            return False

    def mute_volume(self):
        """Mute/unmute system volume"""
        try:
            pyautogui.press('volumemute')
            return True
        except Exception as e:
            print(f"Error muting volume: {e}")
            return False

    def pause_play(self):
        """Pause or play media"""
        try:
            pyautogui.press('playpause')
            return True
        except Exception as e:
            print(f"Error with pause/play: {e}")
            return False

    def play_media(self):
        """Play media"""
        try:
            pyautogui.press('play')
            return True
        except Exception as e:
            # Fallback to space key (common play/pause)
            try:
                pyautogui.press('space')
                return True
            except:
                print(f"Error playing media: {e}")
                return False

    def pause_media(self):
        """Pause media"""
        try:
            pyautogui.press('pause')
            return True
        except Exception as e:
            # Fallback to space key (common play/pause)
            try:
                pyautogui.press('space')
                return True
            except:
                print(f"Error pausing media: {e}")
                return False

    def next_track(self):
        """Skip to next track"""
        try:
            pyautogui.press('nexttrack')
            return True
        except Exception as e:
            print(f"Error skipping to next track: {e}")
            return False

    def previous_track(self):
        """Go to previous track"""
        try:
            pyautogui.press('prevtrack')
            return True
        except Exception as e:
            print(f"Error going to previous track: {e}")
            return False

    def minimize_window(self):
        """Minimize current window"""
        try:
            pyautogui.hotkey('win', 'down')
            return True
        except Exception as e:
            print(f"Error minimizing window: {e}")
            return False

    def maximize_window(self):
        """Maximize current window"""
        try:
            pyautogui.hotkey('win', 'up')
            return True
        except Exception as e:
            print(f"Error maximizing window: {e}")
            return False

    def screenshot(self):
        """Take a screenshot"""
        try:
            # Create screenshots directory if it doesn't exist
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/ss_{timestamp}.png"

            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)

            return f"Screenshot saved successfully!"
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return "Failed to take screenshot"

    def type_text(self, text):
        """Type the specified text"""
        try:
            pyautogui.write(text)
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False

    def press_key(self, key):
        """Press a specific key"""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
            return False

    def hotkey(self, *keys):
        """Press a combination of keys"""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"Error pressing hotkey {keys}: {e}")
            return False

    def copy_to_clipboard(self):
        """Copy selected text to clipboard"""
        try:
            pyautogui.hotkey('ctrl', 'c')
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False

    def paste_from_clipboard(self):
        """Paste from clipboard"""
        try:
            pyautogui.hotkey('ctrl', 'v')
            return True
        except Exception as e:
            print(f"Error pasting from clipboard: {e}")
            return False

    def select_all(self):
        """Select all text"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            return True
        except Exception as e:
            print(f"Error selecting all: {e}")
            return False

    def undo(self):
        """Undo last action"""
        try:
            pyautogui.hotkey('ctrl', 'z')
            return True
        except Exception as e:
            print(f"Error undoing: {e}")
            return False

    def redo(self):
        """Redo last action"""
        try:
            pyautogui.hotkey('ctrl', 'y')
            return True
        except Exception as e:
            print(f"Error redoing: {e}")
            return False

    def alt_tab(self):
        """Switch between applications"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return True
        except Exception as e:
            print(f"Error switching applications: {e}")
            return False

    def new_tab(self):
        """Open new tab"""
        try:
            pyautogui.hotkey('ctrl', 't')
            return True
        except Exception as e:
            print(f"Error opening new tab: {e}")
            return False

    def refresh_page(self):
        """Refresh current page"""
        try:
            pyautogui.press('f5')
            return True
        except Exception as e:
            print(f"Error refreshing page: {e}")
            return False

    def go_back(self):
        """Go back in browser"""
        try:
            pyautogui.hotkey('alt', 'left')
            return True
        except Exception as e:
            print(f"Error going back: {e}")
            return False

    def go_forward(self):
        """Go forward in browser"""
        try:
            pyautogui.hotkey('alt', 'right')
            return True
        except Exception as e:
            print(f"Error going forward: {e}")
            return False
