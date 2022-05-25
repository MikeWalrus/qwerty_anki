## Demo

![Demo](./gif/qwerty.gif)
background image: Ted.ns, CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0>, via Wikimedia Commons

## Quick Start
1. Find your anki [addon
folder](https://addon-docs.ankiweb.net/addon-folders.html), create a new folder and copy everything
there.
2. Build (and optionally install)
[qwerty](https://github.com/MikeWalrus/qwerty).
3. Run Anki. You should see "Enable qwerty" in the "Tools" menu.
4. Either run `qwerty` first before clicking on
"Enable qwerty", or go on to configure the add-on to run it for you.

## Configuration
### `command`
Open up the configuration file via "Tools->Add-ons->Config", and put your
command for running `qwerty` in a terminal in the `"command"` field. It should
be something like this:
```
"command": "alacritty -e qwerty"
```
 assuming
`alacritty` is your terminal emulator, and it accepts the command it will run
through the `-e` argument.  Change `qwerty` to the location of your `qwerty`
binary if you haven't installed it.

If set correctly, when the add-on complains about `qwerty` not running, the
command will be executed and brings up the terminal if you click on the "Open"
button.
