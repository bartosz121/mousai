
# Mousai

Music player built in Python




![Demo img](https://i.imgur.com/6SXn2m5.png)


## Getting started

Clone the project

```bash
  git clone https://github.com/bartosz121/mousai
```

Go to the project directory

```bash
  cd mousai
```

Create new virtual environment

```bash
  python -m venv env
```

Activate environment

```bash
  # on Linux
  source env/bin/activate

  # on Windows
  ./env/Scripts/activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Run music player

```bash
  python mousai/mousai.py
```

## Usage

- Random songs are picked from playlist and added to play queue
- Add songs to your playlist `File` -> `Add songs` / `Add songs from directory`
- Check queue and history in window menu. `File` -> `Show queue` / `Show history`


## Keyboard shortcuts

- `Return` - Start selected song from playlist table
- `M`/`N` - Turn volume up/down
- `Space` - Pause/Resume current song
- `R` - Restart current song

## TODO

- [ ] Delete items from playlist
- [ ] Settings window in `Edit` menu
- [ ] Turn on/off random song picking
- [ ] Turn on/off loop mode of one song