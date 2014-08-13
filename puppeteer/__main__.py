import sys
import yaml
import puppeteer

if len(sys.argv) < 2:
    print("error: no configuration file given".format(sys.argv[0]))
    sys.exit(1)

with open(sys.argv[1]) as config_file:
    config = yaml.safe_load(config_file)

goethe = puppeteer.Puppeteer(config)
goethe.set_up_props()
goethe.perform()

