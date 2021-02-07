$(function() {
    function DevHelperViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];
        self.controlViewModel = parameters[1];

        self.isDisabled = ko.observable(false);
        self.inputModule = ko.observable("");
        self.inputClass = ko.observable("");
        self.inputCacheFilter = ko.observable("");

        self.output = ko.observable("Ready.");

        self.onStartupComplete = function() {
            $("#sidebar_plugin_DevHelper_wrapper > div.accordion-heading > a").prepend("<i class='fab fa-dev'/>");
            self.sidebar = $("#sidebar_plugin_DevHelper_wrapper #dev_helper");

        };

        self.onBeforeBinding = function() {
            window.dev_helper = self;
            var settings = self.settingsViewModel.settings.plugins.DevHelper;

            self.inputModule(settings.last_module());
            self.inputClass(settings.last_class());
            self.inputCacheFilter(settings.last_cache_filter());
        }

        self.saveSettings = function() {
            OctoPrint.settings.savePluginSettings('DevHelper', {
                "last_module": self.inputModule(),
                "last_class": self.inputClass(),
                "last_cache_filter": self.inputCacheFilter()
            });
        }

        self.handleError = function(error) {
            console.error(error);
            self.output("Error: " + error);
        }

        self.sendCmd = function(cmd, params) {
            self.isDisabled(true);
            self.output("> " + cmd + " " + JSON.stringify(params))
            OctoPrint.simpleApiCommand("DevHelper", cmd, params)
                .done(function (res) {
                    if (res && res.error)
                        self.handleError(res.error);
                    else
                        self.output("Done: " + res);
                    self.isDisabled(false);
                })
                .fail(function (res) { self.output("Server error: " + res); self.isDisabled(false); } );
        }

        /* Actions */

        self.handleClearTemplateCache = function() {
            self.saveSettings();
            self.sendCmd("clear_template_cache", {filter: self.inputCacheFilter()});
            return false;
        }

        self.handleReloadClass = function() {
            self.saveSettings();
            self.sendCmd("reload_class", {"module": self.inputModule(), "class": self.inputClass()});
            return false;
        }


    }

    OCTOPRINT_VIEWMODELS.push({
        construct: DevHelperViewModel,
        dependencies: ["settingsViewModel", "controlViewModel"],
        elements: ["#sidebar_plugin_DevHelper"]
    });
});
