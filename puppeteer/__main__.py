from puppeteer import Puppeteer
from puppeteer.config import config

goethe = Puppeteer(config)
goethe.set_up_props()
goethe.perform()

