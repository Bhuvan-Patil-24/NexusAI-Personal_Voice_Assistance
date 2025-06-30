import subprocess
import os
import shutil
import time

class WindowsAppLauncher:
    def __init__(self):
        pass

    def open_app(self, app_name):
        success = False
        
        methods = [
            self._try_path_search,
            self._try_windows_common_paths,
            self._try_windows_methods,
        ]

        if ' ' or '-' or '_' in app_name:
            app_name = app_name.replace(' ', '').replace('-', '').replace('_', '')

        for method in methods:
            try:
                if method(app_name):
                    print(f"Opening {app_name}...")
                    time.sleep(0.1)
                    success = True
                    break  # Exit loop on first success
                else: continue
            except Exception:
                continue  # Continue to next method on failure
        return success

    def _try_path_search(self, app_name):
        try:
            executable = shutil.which(app_name)
            if executable:
                process = subprocess.Popen(
                    [executable],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(0.1)
                if process.poll() is None:
                    return True
        except Exception:
            pass
        return False

    def _try_windows_methods(self, app_name):
        methods = [
            # Try Windows start command
            lambda: subprocess.Popen(
                f'start "" "{app_name}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            ),
            # Try with powershell
            lambda: subprocess.Popen(
                f'powershell -WindowStyle Hidden -Command "Start-Process \'{app_name}\'"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        ]

        for method in methods:
            try:
                process = method()
                if process is None:
                    continue  # If the process didn't start, try the next method
                time.sleep(0.1)
                # For start command, we can't easily check if it worked, so assume success
                return True
            except Exception:
                continue
        return False

    def _try_windows_common_paths(self, app_name):
        try:
            username = os.getenv('USERNAME', 'User')
            paths = [
                f"C:\\Program Files\\{app_name}\\{app_name}.exe",
                f"C:\\Program Files (x86)\\{app_name}\\{app_name}.exe",
                f"C:\\Users\\{username}\\AppData\\Local\\{app_name}\\{app_name}.exe",
                f"C:\\Users\\{username}\\AppData\\Local\\Programs\\{app_name}\\{app_name}.exe",
                f"C:\\Users\\{username}\\AppData\\Roaming\\{app_name}\\{app_name}.exe",
                f"C:\\Program Files\\{app_name}.exe",
                f"C:\\Program Files (x86)\\{app_name}.exe"
            ]

            for path in paths:
                try:
                    if os.path.exists(path):
                        process = subprocess.Popen(
                            [path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        time.sleep(0.1)
                        # Check if process is still running
                        if process.poll() is None:
                            return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

