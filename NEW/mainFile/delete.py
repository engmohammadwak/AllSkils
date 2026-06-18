import os
from colorama import Fore, Style, init

init(autoreset=True)

folders = ["sorted_skills", "logs"]

for folder in folders:
    if not os.path.exists(folder):
        print(Fore.YELLOW + f"Folder '{folder}' does not exist.")
        continue

    exit_code = os.system(f'rmdir /s /q "{folder}"')

    if exit_code == 0 and not os.path.exists(folder):
        print(Fore.GREEN + f"Folder '{folder}' has been deleted.")
    else:
        print(Fore.RED + f"Failed to delete '{folder}'. It may be in use by another process.")