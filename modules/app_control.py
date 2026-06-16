import os
import subprocess
import webbrowser
import platform
import pyautogui
import time
import win32gui
import win32con
import win32api
import win32process
import psutil
import pyperclip
from typing import Optional, Union, List

# Detect OS
SYSTEM_OS = platform.system()  # 'Windows', 'Darwin' (Mac), or 'Linux'

class ApplicationController:
    def __init__(self):
        self.app_map = self._initialize_app_map()
        self.browser_map = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'safari': 'Safari',
            'opera': 'opera.exe',
            'brave': 'brave.exe'
        }
    
    def _initialize_app_map(self) -> dict:
        """Initialize application mappings for different OS"""
        if SYSTEM_OS == 'Windows':
            return {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'outlook': 'outlook.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'file explorer': 'explorer.exe',
                'paint': 'mspaint.exe',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe',
                'task manager': 'taskmgr.exe',
                'control panel': 'control.exe',
                'spotify': 'spotify.exe',
                'vlc': 'vlc.exe',
                'photoshop': 'photoshop.exe',
                'illustrator': 'illustrator.exe',
                'premiere': 'premiere.exe',
                'after effects': 'afterfx.exe',
                'visual studio': 'devenv.exe',
                'vs code': 'code.exe',
                'pycharm': 'pycharm64.exe',
                'intellij': 'idea64.exe',
                'eclipse': 'eclipse.exe',
                'sublime': 'sublime_text.exe',
                'notepad++': 'notepad++.exe',
                'git bash': 'git-bash.exe',
                'docker': 'Docker Desktop.exe',
                'postman': 'Postman.exe',
                'slack': 'slack.exe',
                'teams': 'teams.exe',
                'zoom': 'Zoom.exe',
                'discord': 'Discord.exe',
                'steam': 'steam.exe',
                'epic games': 'EpicGamesLauncher.exe'
            }
        elif SYSTEM_OS == 'Darwin':
            return {
                'safari': 'Safari',
                'chrome': 'Google Chrome',
                'firefox': 'Firefox',
                'terminal': 'Terminal',
                'finder': 'Finder',
                'calculator': 'Calculator',
                'notes': 'Notes',
                'word': 'Microsoft Word',
                'excel': 'Microsoft Excel',
                'powerpoint': 'Microsoft PowerPoint',
                'music': 'Music',
                'photos': 'Photos',
                'system preferences': 'System Preferences',
                'spotlight': 'Spotlight',
                'messages': 'Messages',
                'mail': 'Mail'
            }
        else:  # Linux
            return {
                'firefox': 'firefox',
                'chrome': 'google-chrome',
                'terminal': 'gnome-terminal',
                'calculator': 'gnome-calculator',
                'gedit': 'gedit',
                'files': 'nautilus',
                'spotify': 'spotify',
                'vlc': 'vlc',
                'libreoffice': 'libreoffice',
                'settings': 'gnome-control-center',
                'thunderbird': 'thunderbird'
            }

    def open_application(self, app_name: str) -> str:
        """Opens an application based on the detected operating system"""
        app_name = app_name.lower()
        result = f"Attempting to open {app_name}..."
        
        try:
            if SYSTEM_OS == 'Windows':
                # Check if app is in our map
                for key in self.app_map:
                    if key in app_name:
                        subprocess.Popen(self.app_map[key])
                        return f"Opened {key}"
                
                # If not in map, try to run the command directly
                subprocess.Popen(app_name)
                return result
                
            elif SYSTEM_OS == 'Darwin':
                for key in self.app_map:
                    if key in app_name:
                        os.system(f"open -a '{self.app_map[key]}'")
                        return f"Opened {self.app_map[key]}"
                
                os.system(f"open -a '{app_name}'")
                return result
                
            else:  # Linux
                for key in self.app_map:
                    if key in app_name:
                        subprocess.Popen([self.app_map[key]])
                        return f"Opened {key}"
                
                subprocess.Popen([app_name])
                return result
                
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    def open_website(self, url: str, browser: Optional[str] = None) -> str:
        """Opens a website in the specified or default browser"""
        try:
            # Add http if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if browser and browser.lower() in self.browser_map:
                browser_path = self.browser_map[browser.lower()]
                if SYSTEM_OS == 'Windows':
                    subprocess.Popen([browser_path, url])
                elif SYSTEM_OS == 'Darwin':
                    os.system(f"open -a '{browser_path}' '{url}'")
                else:
                    subprocess.Popen([browser_path, url])
                return f"Opened {url} in {browser}"
            else:
                webbrowser.open(url)
                return f"Opened {url} in default browser"
        except Exception as e:
            return f"Failed to open {url}: {str(e)}"

    def control_application(self, app_name: str, action: Optional[str] = None, 
                          text: Optional[str] = None, keys: Optional[Union[str, List[str]]] = None) -> str:
        """Control applications and perform actions within them"""
        try:
            if SYSTEM_OS == 'Windows':
                # Open the application first
                result = self.open_application(app_name)
                if not result.startswith("Opened"):
                    return result
                
                # Wait for application to open
                time.sleep(2)
                
                # Perform actions if specified
                if action:
                    if action == "write" and text:
                        pyautogui.write(text)
                        return f"Wrote '{text}' in {app_name}"
                    elif action == "press" and keys:
                        if isinstance(keys, str):
                            pyautogui.press(keys)
                        else:
                            for key in keys:
                                pyautogui.press(key)
                        return f"Pressed keys in {app_name}"
                    elif action == "hotkey" and keys:
                        if isinstance(keys, str):
                            pyautogui.hotkey(*keys.split('+'))
                        else:
                            pyautogui.hotkey(*keys)
                        return f"Pressed hotkey in {app_name}"
                    elif action == "click":
                        pyautogui.click()
                        return f"Clicked in {app_name}"
                    elif action == "double_click":
                        pyautogui.doubleClick()
                        return f"Double clicked in {app_name}"
                    elif action == "right_click":
                        pyautogui.rightClick()
                        return f"Right clicked in {app_name}"
                    elif action == "scroll":
                        pyautogui.scroll(int(text) if text else 0)
                        return f"Scrolled in {app_name}"
                    elif action == "copy":
                        pyperclip.copy(text)
                        return f"Copied text to clipboard"
                    elif action == "paste":
                        pyautogui.hotkey('ctrl', 'v')
                        return f"Pasted from clipboard in {app_name}"
                    elif action == "select_all":
                        pyautogui.hotkey('ctrl', 'a')
                        return f"Selected all in {app_name}"
                    elif action == "save":
                        pyautogui.hotkey('ctrl', 's')
                        return f"Saved in {app_name}"
                    elif action == "close":
                        pyautogui.hotkey('alt', 'f4')
                        return f"Closed {app_name}"
                    elif action == "maximize":
                        hwnd = win32gui.GetForegroundWindow()
                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                        return f"Maximized {app_name}"
                    elif action == "minimize":
                        hwnd = win32gui.GetForegroundWindow()
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        return f"Minimized {app_name}"
                    elif action == "restore":
                        hwnd = win32gui.GetForegroundWindow()
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        return f"Restored {app_name}"
                
                return result
            else:
                return "Application control not implemented for this OS"
        except Exception as e:
            return f"Failed to control application: {str(e)}"

    def get_active_window(self) -> str:
        """Get the title of the currently active window"""
        try:
            if SYSTEM_OS == 'Windows':
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            return "Active window detection not implemented for this OS"
        except Exception as e:
            return f"Failed to get active window: {str(e)}"

    def get_running_applications(self) -> List[str]:
        """Get list of currently running applications"""
        try:
            if SYSTEM_OS == 'Windows':
                apps = []
                for proc in psutil.process_iter(['name']):
                    try:
                        apps.append(proc.info['name'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return apps
            return ["Running applications detection not implemented for this OS"]
        except Exception as e:
            return [f"Failed to get running applications: {str(e)}"]

# Create a global instance
app_controller = ApplicationController()

# Expose the main functions
open_application = app_controller.open_application
open_website = app_controller.open_website
control_application = app_controller.control_application
get_active_window = app_controller.get_active_window
get_running_applications = app_controller.get_running_applications 