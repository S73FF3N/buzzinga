# Buzzinga

A fullscreen quiz game for parties and game nights. Supports USB buzzers, multiple game modes, and works on both Linux and Windows.

## Installation

### Starting the setup script on Linux

Do you have uv and git installed? If you are not sure, open a terminal and run these commands one by one:

```bash
sudo apt install git
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

If you already have them, that's fine — they'll just be updated.

Now download Buzzinga and start the setup:

```bash
git clone https://github.com/S73FF3N/buzzinga.git /tmp/buzzinga
cd /tmp/buzzinga
chmod +x setup.sh
./setup.sh
```

### Enabling USB buzzers on Linux (one-time)

On Linux, USB buzzers need a one-time permission rule before any app can read them. Paste this **single line** into a terminal once (it asks for your password once, then prints nothing):

```bash
printf '%s\n' 'SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="1000", MODE="0660", GROUP="plugdev", TAG+="uaccess"' 'KERNEL=="hidraw*", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="1000", MODE="0660", GROUP="plugdev", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/99-buzz.rules >/dev/null && sudo udevadm control --reload-rules && sudo udevadm trigger
```

That's it — your buzzers now work in the game. A few notes:

- Run it **once per computer**. You can run it even before plugging the buzzers in.
- If the buzzers were already plugged in, unplug and replug them once afterwards.
- Without this, the buzzers show up as "not detected" (you can still play with the keyboard).

### Starting the setup script on Windows

First, install these two free tools (if you don't have them already):

1. Download and install **git** from https://git-scm.com/downloads/win
2. Install **uv** by opening **PowerShell** (search "PowerShell" in the Start menu) and running:
   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

Then open **Command Prompt** (search "cmd" in the Start menu) and run these commands one by one:

```
git clone https://github.com/S73FF3N/buzzinga.git %TEMP%\buzzinga
cd %TEMP%\buzzinga
setup.bat
```

### What the setup script does

The setup script will ask you one question: **where do you want Buzzinga installed?** Just press Enter to use the default (a `Buzzinga` folder on your Desktop), or type a different path.

Then it builds everything for you. This takes about a minute the first time — just let it run.

When it's done, you'll have a folder with two things inside:

```
Buzzinga/
├── buzzinga       (the app — double-click this to play!)
└── data/          (your quiz content goes here)
```

On Windows, the app is called `buzzinga.exe`.

That's it! Double-click the app to play. The cloned folder was only needed for the setup — on Linux it's in `/tmp` and gets cleaned up automatically.

## Adding Game Content

Buzzinga doesn't come with quiz content — you bring your own! Open the `data/` folder inside your Buzzinga installation. You'll see these subfolders:

| Folder | What goes in it | Used by |
|--------|----------------|---------|
| `data/images/` | Folders with pictures (one folder per category) | Image Quiz |
| `data/sounds/` | Folders with audio clips (one folder per category) | Audio Quiz |
| `data/hints/` | JSON files with 10 hints per answer | 10 Hints |
| `data/questions/` | JSON files with multiple choice questions | Multiple Choice |
| `data/who-knows-more/` | JSON files with quick-fire questions | Who Knows More? |

Create a subfolder or JSON file for each category you want to play. The category name shown in the game is taken from the folder or file name.

### Example: Hints JSON

Each hint file is a list of entries. Each entry has a solution and 10 hints that gradually make it easier to guess:

```json
[
  {
    "fields": {
      "solution": "Justin Bieber",
      "hint1": "Boyfriend",
      "hint2": "Sorry",
      "hint3": "Yummy",
      "hint4": "Baby",
      "hint5": "I Don't Care",
      "hint6": "Stay",
      "hint7": "Peaches",
      "hint8": "What do you mean?",
      "hint9": "Stuck with you",
      "hint10": "Love Yourself"
    }
  }
]
```

## Game Modes

- **Image Quiz** — an image is revealed step by step, buzz in to guess what it is
- **Audio Quiz** — listen to a sound clip and guess the answer
- **10 Hints** — you get up to 10 hints to figure out the solution
- **Who Knows More?** — answer as many questions as possible before time runs out
- **Multiple Choice** — classic question format with answer options

Supports 2-4 players with USB buzzer input or keyboard controls. Available in English and German.

## Controls

| Key | Action |
|-----|--------|
| **USB Buzzers** | Buzz in |
| **R** | Correct answer |
| **F** | Wrong answer |
| **Escape** | Back / Exit game |
