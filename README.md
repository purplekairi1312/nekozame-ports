# nekozame-ports

Ports, decomps and recomps for GNU/Linux: games rebuilt to run natively, from a reviewed catalog, installed in a step. It comes with [nekozame os](https://github.com/purplekairi1312/nekozame-os), and runs on any other GNU/Linux too.

## What it does

- Installs ports from a [catalog](docs/catalog.md) where each one was looked at before it was added: Ship of Harkinian, Zelda 64: Recompiled, Unleashed Recompiled, sm64coopdx, GZDoom, OpenMW and more.
- Uses Flathub's sandboxed version whenever a port is there. The others come from the project's own GitHub releases.
- Says what each port needs to play, usually your own copy of the game, when you install it and again on its first start.
- Makes a launcher for each port, and adds it to Steam when Steam is there. ES-DE's Ports system can run the launchers.
- Keeps them up to date with `nekozame-ports update`.
- Checks for new ports in the catalog every week and tells you.

## Install

On nekozame os it's already there: `ujust nekozame-ports`.

On any other GNU/Linux, it's one file:

```sh
mkdir -p ~/.local/bin
curl -fLo ~/.local/bin/nekozame-ports https://raw.githubusercontent.com/purplekairi1312/nekozame-ports/main/nekozame-ports
chmod +x ~/.local/bin/nekozame-ports
```

- It needs Python 3, and Flatpak with Flathub for the Flathub ports.
- [gum](https://github.com/charmbracelet/gum) makes the picker nicer, and zenity shows each port's needs on its first start. Both are optional.
- It reads the newest catalog from this repo once a day.

## Use

| Command | What it does |
|---|---|
| `nekozame-ports` | Pick ports to install, the newest first |
| `nekozame-ports list` | Every port in the catalog, and what's installed |
| `nekozame-ports info NAME` | What it plays, what you need, where it's from |
| `nekozame-ports install NAME...` | Install, by name or id |
| `nekozame-ports update` | The installed ones to their newest release |
| `nekozame-ports remove NAME...` | Uninstall |
| `nekozame-ports check` | The newest catalog: new ports, and updates |

How it all works, where game files go, and how to suggest a port: [docs/guide.md](docs/guide.md).

## Safety

- Flathub ports are sandboxed and checked by Flathub.
- GitHub ports run unsandboxed, like any program you download. That's why only reviewed projects are in the catalog.
- A project that isn't in the catalog can still be installed with `nekozame-ports install github:OWNER/REPO`, but only after a warning that nobody has looked at it.

## License

- GPL-3.0-or-later ([LICENSE](LICENSE)).
- The ports are their projects' own work, under their own licenses. nekozame-ports only downloads them from where their projects publish them.
