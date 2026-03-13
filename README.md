# Buzzinga

A fullscreen quiz game for parties and game nights. Supports USB buzzers, multiple game modes, and works on both Linux and Windows.

## Installation

You only need one thing: **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (a Python tool manager). It takes care of everything else for you — Python, dependencies, all of it.

Once you have uv installed, open a terminal and navigate to the folder where you want Buzzinga to live. For example, your Desktop:

```bash
cd ~/Desktop
```

Then download and start Buzzinga:

```bash
git clone https://github.com/S73FF3N/buzzinga.git
cd buzzinga
uv run buzzinga
```

The first time you run this, uv will automatically download Python and install all dependencies. This may take a moment. After that, the game starts instantly.

> From now on, whenever you want to play, just open a terminal, go to your buzzinga folder and run `uv run buzzinga`.

## Setting up with PyInstaller

Don't want to open a terminal every time you play? No problem. You can turn Buzzinga into a regular app — a single file you double-click to start, just like any other program on your computer. This works on both Linux and Windows.

You'll still need uv for this one-time setup, but once you're done you can forget about it.

### Step 1: Download Buzzinga

Open a terminal and run these commands. This downloads Buzzinga to your Desktop (you can pick a different folder if you prefer):

```bash
cd ~/Desktop
git clone https://github.com/S73FF3N/buzzinga.git
cd buzzinga
```

### Step 2: Build the executable

Still in the terminal, run:

```bash
uv run pyinstaller launcher.py --onefile --add-data "src/buzzinga/staticfiles:staticfiles" --name buzzinga --paths src
```

This takes a moment. When it's done, you'll find a new `dist/` folder inside the `buzzinga` folder. Inside `dist/` is your executable — `buzzinga` on Linux, `buzzinga.exe` on Windows.

### Step 3: Set up your game folder

Now create a folder wherever you want Buzzinga to live permanently — for example, a folder called `Buzzinga` on your Desktop. Put two things inside it:

1. The executable you just built (from `dist/`)
2. A folder called `data` — this is where your quiz content goes (see [Adding Game Content](#adding-game-content) below)

It should look like this:

```
Buzzinga/
├── buzzinga          (or buzzinga.exe on Windows)
└── data/
    ├── images/
    ├── sounds/
    ├── hints/
    ├── questions/
    └── who-knows-more/
```

### Step 4: Play!

Double-click the executable to start the game. That's it — no terminal, no Python, no uv needed anymore.

You can now delete the `buzzinga` folder you cloned in Step 1 if you want. Everything you need is in your new game folder.

## Adding Game Content

Buzzinga doesn't come with quiz content — you bring your own! Inside your `buzzinga` folder (or next to your executable) you'll find a `data/` folder. This is where you put your game files:

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

Supports 2–4 players with USB buzzer input or keyboard controls. Available in English and German.

## Controls

| Key | Action |
|-----|--------|
| **USB Buzzers** | Buzz in |
| **R** | Correct answer |
| **F** | Wrong answer |
| **Escape** | Back / Exit game |
