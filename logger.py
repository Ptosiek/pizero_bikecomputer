import logging

app_logger = logging.getLogger("bike_computer")

# change level in regard to config G_DEBUG
app_logger.setLevel(level=logging.INFO)

# Add simple stream handler
sh = logging.StreamHandler()

app_logger.addHandler(sh)
