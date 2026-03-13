# Buzzinga

A fullscreen quiz game for parties and game nights. Supports USB buzzers, multiple game modes, and works on both Linux and Windows.

## Game Modes

- **Image Quiz** — reveal an image step by step, buzz in to guess
- **Audio Quiz** — listen to a sound clip and guess the answer
- **10 Hints** — get up to 10 hints to identify the solution
- **Who Knows More?** — answer as many questions as possible before time runs out
- **Multiple Choice** — classic question format

Supports 2–4 players with USB buzzer input or keyboard controls. Available in English and German.

## Quick Start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.

```bash
git clone https://github.com/S73FF3N/buzzinga.git
cd buzzinga
uv run buzzinga
```

That's it — uv handles the virtual environment and all dependencies automatically.

## Game Data

Place your quiz content in the `data/` folder:

```
data/
├── images/       # folders with images for Image Quiz
├── sounds/       # folders with audio files for Audio Quiz
├── hints/        # JSON files for 10 Hints
├── questions/    # JSON files for Multiple Choice
└── who-knows-more/  # JSON files for Who Knows More
```

### Hint JSON format

```json
[
  {
    "fields": {
      "solution": "Justin Bieber",
      "hint1": "Boyfriend",
      "hint2": "Sorry",
      "hint3": "Yummy",
      ...
      "hint10": "Love Yourself"
    }
  }
]
```

## Controls

| Key | Action |
|-----|--------|
| **USB Buzzers** | Buzz in |
| **R** | Correct answer |
| **F** | Wrong answer |
| **Escape** | Back / Exit game |

## Building a Windows Executable

```bash
uv run pyinstaller buzzinga_class.py --onefile --add-data "src/buzzinga/staticfiles:staticfiles"
```
