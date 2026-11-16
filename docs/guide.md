# How nekozame-ports works

## Ports, decomps and recomps

All of them are games that run natively on your computer, without an emulator:

- **Decomp:** a console game's code rebuilt by hand into source code, then built for PC. Ship of Harkinian (Ocarina of Time) and sm64coopdx (Super Mario 64) are decomps.
- **Recomp:** a console game's code translated automatically into PC code. Zelda 64: Recompiled and Unleashed Recompiled are recomps.
- **Source port:** an old PC game whose source code was released, made to run on today's systems. GZDoom, Ironwail (Quake) and Dhewm 3 (Doom 3) are source ports.
- **Reimplementation:** a game's engine written again from scratch. OpenMW (Morrowind), OpenRCT2 and DevilutionX (Diablo) are reimplementations.

None of them include the game itself, apart from the free ones. You play with your own copy.

## Installing a port

```sh
nekozame-ports
```

A list of everything in the catalog that you don't have yet, newest first. Pick with space, install with enter.

For each port, it:

1. Says what you need to play it.
2. Installs it: from Flathub if the port is there, or else the newest release from the project's GitHub page. A release can be a Flatpak bundle, an AppImage, or an archive with the program in it. It picks the GNU/Linux build for x86-64.
3. Makes a launcher script in `~/.local/share/nekozame/ports/launchers`, named like the port.
4. Adds it to Steam if Steam is running. nekozame os puts it in Steam's Ports tab with its art; on SteamOS or Bazzite it uses their own tool; elsewhere add it yourself with Steam → Add a Game → Add a Non-Steam Game.

## Game files

Most ports need your own copy of the game. `nekozame-ports info NAME` and the [catalog](catalog.md) say what each one needs:

- **A ROM** for the console decomps and recomps. Most ask for it on first start and make their own game file from it (Ship of Harkinian, Zelda 64: Recompiled, sm64coopdx...). It has to be the version the catalog names, usually the USA one.
- **The game's files** for the source ports and reimplementations: WAD files for Doom, Quake's id1 folder, Morrowind's data files, DIABDAT.MPQ for Diablo...
- **Nothing** for a few: Sonic Robo Blast 2, OpenTTD and OpenTyrian come with free game data.

On a port's first start, its launcher shows what it needs once (if zenity is installed). Where to put the files is on each port's page when it doesn't ask for them itself.

## ES-DE

ES-DE has a Ports system that runs scripts. nekozame os sets it up to read `~/.local/share/nekozame/ports/launchers`. On another system, point ES-DE's `ports` folder there, or copy the launchers into it.

## Updating and removing

- `nekozame-ports update` updates Flathub ports with Flatpak, and reinstalls a GitHub port when its project has a newer release.
- `nekozame-ports remove NAME` uninstalls a port, its launcher and its menu entry. Your game files and saves, which the port keeps in its own folders, stay.
- `nekozame-ports check` gets the newest catalog and tells you about ports added since you last looked. nekozame os runs it every week.

## Where it keeps things

| | |
|---|---|
| `~/.local/share/nekozame/ports/` | The GitHub ports that aren't Flatpaks, one folder each |
| `~/.local/share/nekozame/ports/launchers/` | One launcher script per port |
| `~/.local/share/applications/nekozame-port-*.desktop` | Menu entries for the non-Flatpak ports |
| `~/.local/state/nekozame/ports.json` | What's installed, and which version |
| `~/.cache/nekozame-ports/catalog.json` | The newest catalog, read once a day |

## Suggesting a port

Open an issue or a pull request on [nekozame-ports](https://github.com/purplekairi1312/nekozame-ports) with the port's page. For a pull request, add it to `catalog.json`:

```json
{
  "id": "short-name",
  "name": "The port's name",
  "plays": "The game it plays",
  "system": "The console it's from, or PC",
  "kind": "decomp, recomp, source port, reimplementation or fan game",
  "source": "github:OWNER/REPO or flathub:APP.ID",
  "needs": "What you need to play it, and where it goes",
  "page": "https://..."
}
```

- An `"asset"` with a regular expression picks the right download when a release has several GNU/Linux builds.
- Run `tools/catalog.py doc` to update this site's catalog page, and `tools/catalog.py validate` to check.

Before a port is added, someone looks at it:

- It's a real port of the game it names, by the people the page says.
- Its newest release has a GNU/Linux build for x86-64 that starts.
- What it needs to play is known and written in `needs`.
- If it's on Flathub, the Flathub version is used.

## The weekly checks

GitHub checks the catalog every Monday:

- **Downloads:** each port's download is still there. If one broke (a project renamed its files, or stopped making GNU/Linux builds), an issue says which.
- **Candidates:** it searches GitHub and Flathub for projects that look like ports, have a GNU/Linux build, and aren't in the catalog yet. One issue lists them, kept up to date. They're for looking at, not installed for anyone.
