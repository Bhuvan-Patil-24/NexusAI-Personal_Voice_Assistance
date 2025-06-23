import subprocess
import platform
import os

# Desktop applications dictionary with cross-platform support
DESKTOP_APPS = {
    # Browsers
    'chrome': {
        'windows': 'chrome',
        'mac': 'open -a "Google Chrome"',
        'linux': 'google-chrome'
    },
    'firefox': {
        'windows': 'firefox',
        'mac': 'open -a Firefox',
        'linux': 'firefox'
    },
    'edge': {
        'windows': 'msedge',
        'mac': 'open -a "Microsoft Edge"',
        'linux': 'microsoft-edge'
    },
    
    # Text Editors & IDEs
    'vscode': {
        'windows': 'code',
        'mac': 'code',
        'linux': 'code'
    },
    'notepad': {
        'windows': 'notepad',
        'mac': 'open -a TextEdit',
        'linux': 'gedit'
    },
    'sublime': {
        'windows': 'subl',
        'mac': 'subl',
        'linux': 'subl'
    },
    
    # Media Players
    'vlc': {
        'windows': 'vlc',
        'mac': 'open -a VLC',
        'linux': 'vlc'
    },
    'spotify': {
        'windows': 'spotify',
        'mac': 'open -a Spotify',
        'linux': 'spotify'
    },
    
    # Office Apps
    'word': {
        'windows': 'winword',
        'mac': 'open -a "Microsoft Word"',
        'linux': 'libreoffice --writer'
    },
    'excel': {
        'windows': 'excel',
        'mac': 'open -a "Microsoft Excel"',
        'linux': 'libreoffice --calc'
    },
    'powerpoint': {
        'windows': 'powerpnt',
        'mac': 'open -a "Microsoft PowerPoint"',
        'linux': 'libreoffice --impress'
    },
    
    # System Apps
    'calculator': {
        'windows': 'calc',
        'mac': 'open -a Calculator',
        'linux': 'gnome-calculator'
    },
    'terminal': {
        'windows': 'cmd',
        'mac': 'open -a Terminal',
        'linux': 'gnome-terminal'
    },
    'file_manager': {
        'windows': 'explorer',
        'mac': 'open -a Finder',
        'linux': 'nautilus'
    },
    
    # Communication
    'discord': {
        'windows': 'discord',
        'mac': 'open -a Discord',
        'linux': 'discord'
    },
    'slack': {
        'windows': 'slack',
        'mac': 'open -a Slack',
        'linux': 'slack'
    },
    'zoom': {
        'windows': 'zoom',
        'mac': 'open -a zoom.us',
        'linux': 'zoom'
    },
    
    # Development Tools
    'git_bash': {
        'windows': 'git-bash',
        'mac': 'open -a Terminal',
        'linux': 'gnome-terminal'
    },
    'docker': {
        'windows': 'docker',
        'mac': 'open -a Docker',
        'linux': 'docker'
    }
}

def get_os():
    """Get the current operating system"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'mac'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'

def open_app(app_name):
    """Open a desktop application by name"""
    current_os = get_os()
    
    if app_name.lower() not in DESKTOP_APPS:
        print(f"App '{app_name}' not found in the dictionary")
        return False
    
    try:
        command = DESKTOP_APPS[app_name.lower()][current_os]
        
        if current_os == 'windows':
            subprocess.Popen(command, shell=True)
        else:
            subprocess.Popen(command.split())
        
        print(f"Opening {app_name}...")
        return True
        
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        return False

# Usage examples:
if __name__ == "__main__":
    # Open Chrome
    open_app('chrome')
    
    # Open VS Code
    open_app('vscode')
    
    # Open Calculator
    open_app('calculator')
    
    # List available apps
    print("\nAvailable apps:")
    for app in DESKTOP_APPS.keys():
        print(f"- {app}")