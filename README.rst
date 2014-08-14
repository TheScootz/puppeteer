**This is currently unreleased software. The software will change significantly before release.**

Puppeteer
---------

Puppeteer is a minimal Python-based IRC bot, available under the GNU Public License, version 3.

Installation
------------

Puppeteer will be available as a Python package in the future. For now, you may install the development branch.

To install and run the development branch::

  pip install PyYAML
  git clone https://github.com/TheScootz/pybot
  cd pybot
  editor config.yaml # edit the configuration using your favorite editor
  python -m puppeteer config.yaml

Adding functionality
--------------------

Puppeteer can run many bots, called puppets, and each bot connects to one network.

Each of these puppets has a collection of scripts, called stageprops, that add functionality to the bot.

To add a stageprop, add the script file to the puppeteer/stageprops/ directory.  Edit your configuration file
to include the name of the script (excluding the .py suffix) under the top-level stageprops key.  Then for each
puppet you'd like the script enabled on, add it to their sub-configuration.
