# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


import octoprint.plugin
import octoprint.vendor
import os
import flask
import time
import sys
import importlib
import traceback
import gc


def format_exception(err):
    tb = err.__traceback__
    return "%s: %s (%s, %s line %s)" % (
        type(err).__name__, str(err), os.path.basename(tb.tb_frame.f_code.co_filename), tb.tb_frame.f_code.co_name, tb.tb_lineno
    )


def reload_module(module_name):
    module_before = sys.modules.pop(module_name, None)
    try:
        if "." not in module_name:  # It's a package
            module = octoprint.vendor.imp.load_package(module_name, module_before.__path__[0])
        else:
            module = importlib.import_module(module_name)
    except Exception as err:
        sys.modules[module_name] = module_before
        raise err
    sys.modules[module_name] = module
    return module


class DevHelperPlugin(octoprint.plugin.SettingsPlugin, octoprint.plugin.AssetPlugin, octoprint.plugin.TemplatePlugin, octoprint.plugin.SimpleApiPlugin, octoprint.plugin.UiPlugin):
    def __init__(self):
        pass

    def get_assets(self):
        return dict(js=["js/dev_helper.js"], css=["css/dev_helper.css"])

    def get_template_configs(self):
        return [
            dict(type="sidebar", name="Dev Helper", template="dev_helper_sidebar.jinja2", custom_bindings=False)
        ]

    def get_settings_defaults(self):
        return {
            "last_module": "",
            "last_class": "",
            "last_cache_filter": ""
        }

    def get_template_vars(self):
        return {}

    def get_update_information(self):
        return dict(
            devhelper=dict(
                displayName="Dev Helper",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="clonesht",
                repo="OctoPrint-DevHelper",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/clonesht/OctoPrint-DevHelper/archive/{target_version}.zip"
            )
        )

    def get_api_commands(self):
        return {
            "eval": ["cmd"],
            "reload_class": ["module", "class"],
            "clear_template_cache": ["filter"]
        }

    def on_api_command(self, command, data):
        if not octoprint.access.permissions.Permissions.ADMIN.can():
            return flask.make_response("Insufficient rights", 403)

        try:
            if command == "eval":
                return self.action_eval(data["cmd"])
            elif command == "clear_template_cache":
                back = self.action_clear_template_cache(data["filter"])
            elif command == "reload_class":
                back = self.action_reload_class(data["module"], data["class"])
        except Exception:
            back = {"error": traceback.format_exc()}

        return flask.jsonify(back)

    def is_api_adminonly(self):
        return True

    # -- API Commands --

    def action_eval(self, cmd):
        # raise Exception("Disabled by default")  # Only enable this function if you know what are you doing

        s = time.time()
        res = eval(cmd)
        print(" > Eval: %s, res: %s (Done in %.3fs)" % (cmd, res, time.time() - s))
        try:
            return flask.jsonify(res)
        except Exception:
            return flask.jsonify(str(res))

    def action_clear_template_cache(self, filter):
        cache = octoprint.server.app.jinja_env.cache
        keys_to_clear = [key for key, val in cache.items() if filter in val.filename]
        for key in keys_to_clear:
            del(cache[key])
        return "Cleared template cache: %s" % len(keys_to_clear)

    def action_reload_class(self, module_name, class_name):
        if module_name not in sys.modules:
            raise Exception("Module %s not loaded" % class_name)

        module = reload_module(module_name)

        patched_num = 0
        for obj in gc.get_objects():
            if type(obj).__name__ == class_name:
                obj.__class__ = getattr(module, class_name)
                patched_num += 1

        return "Reloaded object: %s" % patched_num


__plugin_name__ = "Dev Helper"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Live reload of jinja templates and python source code without restarting OctoPrint."
__plugin_pythoncompat__ = ">=3,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = DevHelperPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
