# 📺 New Season Soon for Kometa

Inspired by [PATTRMM](https://github.com/InsertDisc/pattrmm) this simplifed script checks your [Sonarr](https://sonarr.tv/) for TV Shows for which a new season is airing within a chosen amount of days and creates .yml files which can be used by [Kometa](https://kometa.wiki/) to create a collection and overlays.

![Image](https://github.com/user-attachments/assets/d8aefff5-4c91-449a-a2f3-c96b97aa2721)
---

## ✨ Features
- 🔍 **Detects upcoming Season**: Searches Sonarr for Shows with upcoming seasons
-  ▼ **Filters out unmonitored**: Skips show if season/episode is unmonitored. (optional)
-  🪄 **Customizable**: Change date format, collection name, overlay positioning, text, ..
- ℹ️ **Informs**: Lists matched and skipped(unmonitored) TV shows.
- 📝 **Creates .yml**: Creates a collection and overlay file which can be used with Kometa.

---

## 🛠️ Installation

### 1️⃣ Download the script
Clone the repository:
```sh
git clone https://github.com/netplexflix/New-Season-Soon-for-Kometa.git
cd New-Season-Soon-for-Kometa
```

![#c5f015](https://placehold.co/15x15/c5f015/c5f015.png) Or simply download by pressing the green 'Code' button above and then 'Download Zip'.

### 2️⃣ Extract or move the files to a 'NSSK' subfolder in your Kometa config folder
- Go to your Kometa install folder, then config.
- Create a subfolder named NSSK.
- Put the files in this subfolder. (`config.yml`, `NSSK.py` and `requirements.txt`)

### 3️⃣ Install Dependencies
- Ensure you have [Python](https://www.python.org/downloads/) installed (`>=3.8` recommended). <br/>
- Open a Terminal in the script's directory
>[!TIP]
>Windows Users: <br/>
>Go to the NSSK folder (where NSSK.py is). Right mouse click on an empty space in the folder and click `Open in Windows Terminal`
- Install the required dependencies by pasting the following code:
```sh
pip install -r requirements.txt
```

### 4️⃣ Edit your Kometa config
- Open your Kometa config.yml (config/config.yml, NOT config/NSSK/config.yml)
- Under your TV Show library settings, add the paths to `NSSK_TV_COLLECTION.yml` and `NSSK_TV_OVERLAYS.yml` (These files will be created in your NSSK folder when you run the script).<br/>
  Example:
  ```
  TV Shows:
    collection_files:
    - file: P:/Kometa/config/NSSK/NSSK_TV_COLLECTION.yml
    overlay_files:
    - file: P:/Kometa/config/NSSK/NSSK_TV_OVERLAYS.yml
  ```
>[!NOTE]
>If you don't want to create a collection and only overlays you can ofcourse skip adding the collection file to your Kometa config.<br/>
>Or the other way around..
---

## ⚙️ Configuration
Edit the `config.yml` file in your NSSK folder and edit the settings:

- **sonarr_url:** Change if needed.
- **sonarr_api_key:** Can be found in Sonarr under settings => General => Security.
- **future_days:** How many days into the future the script should look for season premieres.
- **skip_unmonitored:** Default `true` will skip a show if the upcoming season/episode is unmonitored.
- **collection_name:** The name of the collection.
- **sort_title:** Collection sort title.
- **backdrop:** Change backdrop (the colored banner behind the text) size, color and positioning. [More info here](https://kometa.wiki/en/latest/files/overlays/?h=overlay#backdrop-overlay)
- **text:** Change text color and positioning. [More info here](https://kometa.wiki/en/latest/files/overlays/?h=overlay#text-overlay)
  - **date_format:** The date format to be used on the overlays. e.g.: "yyyy-mm-dd", "mm/dd", "dd/mm", etc.
  - **use_text:** Text to be used on the overlays before the date. e.h.: "NEW SEASON"

>[!NOTE]
> These are date formats you can use:<br/>
> `d`: 1 digit day (1)<br/>
> `dd`: 2 digit day (01)<br/>
> `ddd`: Abbreviated weekday (Mon)<br/>
> `dddd`: Full weekday (Monday)<br/>
><br/>
> `m`: 1 digit month (1)<br/>
> `mm`: 2 digit month (01)<br/>
> `mmm`: Abbreviated month (Jan)<br/>
> `mmmm`: Full month (January)<br/>
><br/>
> `yy`: Two digit year (25)<br/>
> `yyyy`: Full year (2025)
>
>Dividers can be `/`, `-` or a space

---
## 🚀 Usage - Running the Script

Open a Terminal in your script directory and launch the script with:
```sh
python NSSK.py
```
The script will list matched and/or skipped shows and create the .yml files. <br/>
The previous configuration will be erased so Kometa will automatically remove overlays for shows that no longer match the criteria.

> [!TIP]
> Windows users can create a batch file to quickly launch the script.<br/>
> Type `"[path to your python.exe]" "[path to the script]" -r pause"` into a text editor
>
> For example:
> ```
>"C:\Users\User1\AppData\Local\Programs\Python\Python311\python.exe" "P:\Kometa\config\NSSK\NSSK.py" -r
>pause
> ```
> Save as a .bat file. You can now double click this batch file to directly launch the script.<br/>
> You can also use this batch file to [schedule](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10) the script to run.
---


### ⚠️ **Do you Need Help or have Feedback?**
- Join the [Discord](https://discord.gg/VBNUJd7tx3).
- Open an [Issue](https://github.com/netplexflix/New-Season-Soon-for-Kometa/issues) on GitHub.


---
## ？ FAQ
**Is there a docker container?**<br/>
I made this for my personal use. I don't use docker myself and have no plans atm to learn how to make dockerfiles.<br/>
If anyone wants to help make one, please feel free to create a pull request!
  
---  
### ❤️ Support the Project
If you like this project, please ⭐ star the repository and share it with the community!

<br/>

[!["Buy Me A Coffee"](https://github.com/user-attachments/assets/5c30b977-2d31-4266-830e-b8c993996ce7)](https://www.buymeacoffee.com/neekokeen)
