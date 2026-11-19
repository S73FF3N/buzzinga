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
| `data/sort/` | JSON files with elements to sort by a value | Sort it! |

Create a subfolder or JSON file for each category you want to play. The category name shown in the game is taken from the folder or file name.

If a JSON file cannot be read (e.g. a missing comma), its category shows a red **!** instead of the round count. Entries with missing fields are skipped; the round count on the category button only counts complete entries.

### Image Quiz and Audio Quiz files

Every file in a category folder is one round, and its **file name is the answer**:

- `_` becomes a space, `zzz` becomes `(` and `uuu` becomes `)`. So `Take_On_Me_zzzLiveuuu.jpg` is shown as "Take On Me (Live)".
- A file whose name ends in `_example` (e.g. `Eiffel_Tower_example.jpg`) is always played first, as a warm-up round.
- A file with the same name plus `_solution` is shown or played together with the answer and is not a round of its own:
  - Image Quiz: `Eiffel_Tower_solution.jpg` (an image or a video)
  - Audio Quiz: `Take_On_Me_solution.mp3` (a sound) and/or `Take_On_Me_solution.jpg` (an image)

Supported formats (upper or lower case):

| Quiz | Rounds | Solution files |
|------|--------|----------------|
| Image Quiz | `.png` `.jpg` `.jpeg` `.bmp` `.webp` `.avif`, videos `.mp4` `.mov` `.avi` `.webm` `.mkv` | same as rounds |
| Audio Quiz | `.wav` `.mp3` | sounds `.wav` `.mp3`, images `.jpg` `.jpeg` `.png` `.bmp` |

Your files are only read, never changed. If a file cannot be loaded, the game shows its name and skips to the next round on Enter.

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

### Example: Sort JSON

Each entry is one round. The `reference` element is already placed when the round starts; players insert the `elements` one by one. `value` decides the correct order, with the largest value on top (set `"descending": false` to put the smallest on top). Values stay hidden until the round ends. `top_label` and `bottom_label` appear as arrow banners at both ends of the list so players see which direction means what (e.g. "more people" / "fewer people", "older" / "younger"); without them the banners read "mehr" / "weniger". `unit` is appended to the revealed values; an element can set `display` to show a custom text instead.

```json
[
  {
    "criterion": "Population",
    "top_label": "more people",
    "bottom_label": "fewer people",
    "unit": "M",
    "reference": {"name": "Switzerland", "value": 8.96},
    "elements": [
      {"name": "Germany", "value": 83.4},
      {"name": "France", "value": 68.4},
      {"name": "Austria", "value": 9.16},
      {"name": "Luxembourg", "value": 0.67, "display": "about 670,000"}
    ]
  }
]
```

## Game Modes

- **Image Quiz** — an image is revealed step by step, buzz in to guess what it is
- **Audio Quiz** — listen to a sound clip and guess the answer
- **10 Hints** — you get up to 10 hints to figure out the solution
- **Who Knows More?** — answer as many questions as possible before time runs out
- **Multiple Choice** — classic question format with answer options
- **Sort it!** — players take turns inserting elements into a sorted list; a wrong slot knocks you out for the round (no buzzers needed)

Supports 2-4 players with USB buzzer input or keyboard controls. Available in English and German.

## Controls

| Key | Action |
|-----|--------|
| **USB Buzzers** | Buzz in |
| **Enter** | Next step: start the round, nobody buzzed, show the solution, next round |
| **R** | Correct answer |
| **F** | Wrong answer |
| **S** | Image Quiz with reveal animation: reveal the rest of the image faster |
| **P** | Image Quiz: replay the video · Audio Quiz: replay the sound |
| **N** | 10 Hints: show the next hint |
| **Escape** | Back / Exit game |

The settings screen before each game lists the keys for the chosen game mode.

In **Sort it!** each player has 20 seconds. The game master types the number of the chosen element and presses Enter, then types the slot number (shown in the yellow circles) and presses Enter. The game checks the placement itself. **Backspace** deletes input or deselects the element, **F** knocks out a player who has no answer.

## Development

Run the game from a clone of the repository without building it:

```bash
uv run buzzinga
```

It uses the `data/` and `staticfiles/` folders of the repository. Run the tests with:

```bash
uv run pytest
```

They run headless and also run on GitHub for every pull request. To build the executable, use `setup.sh` / `setup.bat`; they contain the PyInstaller options the game needs (bundled `staticfiles/`, and the `imageio` metadata for video playback).
