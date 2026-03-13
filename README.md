# Buzzinga

A fullscreen quiz game for parties and game nights. Supports USB buzzers, multiple game modes, and works on both Linux and Windows.

## Installation

Before you start, install these two free tools:

1. **[git](https://git-scm.com/downloads)** — to download Buzzinga
2. **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — to build it (it handles Python and all dependencies for you)

Then follow the guide for your system below. The setup script will ask you where to install Buzzinga (defaults to your Desktop) and build a standalone app you can double-click to play.

### Linux

Open a terminal and run:

```bash
git clone https://github.com/S73FF3N/buzzinga.git
cd buzzinga
chmod +x setup.sh
./setup.sh
```

### Windows

Open **Command Prompt** or **PowerShell** and run:

```
git clone https://github.com/S73FF3N/buzzinga.git
cd buzzinga
setup.bat
```

### After setup

When the script is done, you'll have a folder (e.g. on your Desktop) with the Buzzinga app inside it. Double-click `buzzinga` (Linux) or `buzzinga.exe` (Windows) to play — no terminal needed anymore.

You can delete the `buzzinga` folder you cloned during setup. You won't need it again unless you want to rebuild.

## Adding Game Content

Buzzinga doesn't come with quiz content — you bring your own! Inside your Buzzinga folder you'll find a `data/` folder. This is where you put your game files:

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
