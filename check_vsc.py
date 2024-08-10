import pyautogui
import pygetwindow as gw
import time
import argparse

def find_vscode_window():
    """Find the VS Code window."""
    windows = gw.getWindowsWithTitle('Visual Studio Code')
    if windows:
        return windows[0]
    return None

def open_extension_and_paste_text(requirement_name, app_name, frontend, backend, style):
    # Find the VS Code window
    vscode_window = find_vscode_window()
    if not vscode_window:
        print("VS Code window not found.")
        return

    # Activate the VS Code window
    vscode_window.activate()
    time.sleep(2)  # Wait for the window to activate

    # Open the "Claude Dev" extension
    pyautogui.hotkey('ctrl', 'shift', 'P')  # Open the command palette
    time.sleep(2)

    pyautogui.typewrite('Claude Dev: Focus on View')  # Type extension name
    time.sleep(2)
    pyautogui.press('enter')  # Open the extension
    time.sleep(5)

    # Read content from the text file
    # content = f'''Can you read {requirement_name}.txt in this folder and create the entire application using {frontend} frontend, {backend} backened with Material UI and compatible backend database. Make sure you create a folder "Warranty-Wiz-application" inside the current folder with 2 subfolders "{frontend}-frontend" and "{backend}-backend" it, place the corresponding components in those subfolders'''
    content = f'''Can you read {requirement_name}.txt in this folder and create the entire application using {frontend} frontend, {backend} backened with {style} and compatible backend database. Make sure you create a folder "{app_name}" inside the current folder with 2 subfolders "{frontend}-frontend" and "{backend}-backend", place the corresponding components in those subfolders'''

    typing_speed = 700  # Characters per minute
    interval = 60 / typing_speed  # Interval between keystrokes

    # Type the content into the text box
    pyautogui.typewrite(content, interval=interval) 

    # Press Enter after the content is fully typed
    pyautogui.press('enter')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass dynamic arguments to the script.")
    parser.add_argument('requirement_name', type=str, help="The name of the requirement file.")
    parser.add_argument('application_name', type=str, help="The name of the application")
    parser.add_argument('tech_stake', type=str, help="The tech stack to use.")
    parser.add_argument('programming_lan', type=str, help="The programming language to use.")
    parser.add_argument('style', type=str, help="The styling to use.")
    
    args = parser.parse_args()
    
    open_extension_and_paste_text(args.requirement_name, args.application_name, args.tech_stake, args.programming_lan, args.style)