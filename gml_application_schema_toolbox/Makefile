# global

PLUGINNAME = gml_application_schema_toolbox

PY_FILES = main.py __init__.py model_dialog.py core/*.py gui/*.py

EXTRAS = Changelog *.svg metadata.txt viewers/*.py viewers/*.svg conf/*.xml gui/*.qml
EXTLIBS = extlibs/*

UI_FILES = ui/*.ui

VERSION=$(shell grep "version=" metadata.txt | cut -d'=' -f 2)

ifeq ($(OS),Windows_NT)
UNAME_S := Windows
else
UNAME_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')
endif

ifeq ($(UNAME_S),Darwin)
PLUGINS_DIR=$(HOME)/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins
else
PLUGINS_DIR=$(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins
endif

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis2/python/plugins
deploy: transcompile
	mkdir -p $(PLUGINS_DIR)/$(PLUGINNAME)
ifeq ($(UNAME_S),Darwin)
	gcp --parents -vfR $(PY_FILES) $(PLUGINS_DIR)/$(PLUGINNAME)
	gcp --parents -vfR $(UI_FILES) $(PLUGINS_DIR)/$(PLUGINNAME)
	gcp --parents -vfRa $(EXTRAS) $(PLUGINS_DIR)/$(PLUGINNAME)
	gcp --parents -vfRaL $(EXTLIBS) $(PLUGINS_DIR)/$(PLUGINNAME)
else
	cp --parents -vfR $(PY_FILES) $(PLUGINS_DIR)/$(PLUGINNAME)
	cp --parents -vfR $(UI_FILES) $(PLUGINS_DIR)/$(PLUGINNAME)
	cp --parents -vfRa $(EXTRAS) $(PLUGINS_DIR)/$(PLUGINNAME)
endif

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(PLUGINS_DIR)/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(PLUGINS_DIR)/$(PLUGINNAME) -iname "__pycache__" -delete
	find $(PLUGINS_DIR)/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;
ifeq ($(UNAME_S),Darwin)
	find $(PLUGINS_DIR)/$(PLUGINNAME) -iname "*.DS_Store" -delete
endif

# The derase deletes deployed plugin
derase:
	rm -Rf $(PLUGINS_DIR)/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: derase deploy dclean
	echo $(VERSION)
	rm -f $(PLUGINNAME)*.zip
	cd $(PLUGINS_DIR); zip -9r $(CURDIR)/$(PLUGINNAME)-$(VERSION).zip $(PLUGINNAME)

upload: zip
	sed s/_VERSION_/$(VERSION)/g < plugins.xml.tmpl > plugins.xml
	scp plugins.xml hekla:~/brgm_gml
	scp $(PLUGINNAME)-$(VERSION).zip hekla:~/brgm_gml/plugins

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

