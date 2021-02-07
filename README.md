# Dev Helper

Live and instant reload of Jinja templates and Python source code without restarting OctoPrint.

![screenshot](screenshot.png)


## Motivation

During plugin development, I found it slow and frustrating to restarting OctoPrint after every modification.


## Setup

Install via the bundled [Plugin Manager](https://plugins.octoprint.org/)
or manually using this URL:

    https://github.com/clonesht/OctoPrint-DevHelper/archive/main.zip


## Usage


### Reload jinja template

 - Modify the template files
 - Enter a part of the local fs path of the template file you want to reload to the `Part of template file path` field.
   (eg. `dev_helper` if you want to reload ~/.octoprint/plugins/DevHelper/templates/dev_helper_sidebar.jinja2 file.)
 - Hit the `Clear cache` button.
 - It should display `Done: Cleared template cache: 1` at the bottom of the sidebar widget.
 - When reloading the page you should see the effect of the modifications immediately.


### Reload python source code

 - Modify .py files
 - Enter the module (package) name of the plugin you want to reload. (eg. DevHelper)
 - Enter the class name from the module you want to update in the memory. (eg. DevHelperPlugin)
 - Hit the `Reload class` button.
 - It should display `Done: Reloaded object: 1` at the bottom of the sidebar widget.
 - It will reload the module, then update the class instances function source code with the updated one.
 - **Note:** It won't `__init__` the class instances again, so it's not 100% solution, but should be fine in most cases.


### Remote eval console (disabled by default)

 - Remove the blocking exception from the eval API command
 - Reload the plugin using Module: `dev_helper`, Class name: `DevHelperPlugin` or restart OctoPrint
 - Run command from JS console using `res = await OctoPrint.simpleApiCommand("DevHelper", "eval", {"cmd": "dir(self)"})`

