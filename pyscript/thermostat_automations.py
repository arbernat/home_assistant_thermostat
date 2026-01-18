# Schedule for Becky's thermostat
@time_trigger("cron(30 6 * * 1-5)")
def becky_morning_normal_weekday():
    """Set Becky's thermostat to Normal at 6:30am on weekdays"""
    log.info("Setting Becky thermostat to Normal (6:30am weekday schedule)")
    input_select.select_option(entity_id="input_select.temperature_becky", option="Normal")

@time_trigger("cron(30 7 * * 0,6)")
def becky_morning_normal_weekend():
    """Set Becky's thermostat to Normal at 7:30am on weekends"""
    log.info("Setting Becky thermostat to Normal (7:30am weekend schedule)")
    input_select.select_option(entity_id="input_select.temperature_becky", option="Normal")

@time_trigger("cron(0 20 * * *)")
def becky_evening_cold():
    """Set Becky's thermostat to Cold at 8pm"""
    log.info("Setting Becky thermostat to Cold (8pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_becky", option="Cold")


# Schedule for Danny's thermostat
@time_trigger("cron(30 6 * * 1-5)")
def danny_morning_weekday():
    """Set Danny's thermostat to Normal at 6:30am on weekdays"""
    log.info("Setting Danny thermostat to Normal (6:30am weekday schedule)")
    input_select.select_option(entity_id="input_select.temperature_danny", option="Normal")

@time_trigger("cron(30 7 * * 0,6)")
def danny_morning_weekend():
    """Set Danny's thermostat to Normal at 7:30am on weekends"""
    log.info("Setting Danny thermostat to Normal (7:30am weekend schedule)")
    input_select.select_option(entity_id="input_select.temperature_danny", option="Normal")

@time_trigger("cron(0 22 * * *)")
def danny_evening():
    """Set Danny's thermostat to Normal at 10pm"""
    log.info("Setting Danny thermostat to Normal (10pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_danny", option="Normal")


# Schedule for Upstairs thermostat
@time_trigger("cron(30 6 * * 1-5)")
def upstairs_morning_occupied_weekday():
    """Set Upstairs thermostat to Occupied at 6:30am on weekdays"""
    log.info("Setting Upstairs thermostat to Occupied (6:30am weekday schedule)")
    input_select.select_option(entity_id="input_select.temperature_upstairs", option="Normal")

@time_trigger("cron(0 7 * * 0,6)")
def upstairs_morning_occupied_weekend():
    """Set Upstairs thermostat to Occupied at 7am on weekends"""
    log.info("Setting Upstairs thermostat to Occupied (7am weekend schedule)")
    input_select.select_option(entity_id="input_select.temperature_upstairs", option="Normal")

@time_trigger("cron(0 9 * * *)")
def upstairs_morning_unoccupied():
    """Set Upstairs thermostat to Unoccupied at 9am"""
    log.info("Setting Upstairs thermostat to Unoccupied (9am schedule)")
    input_select.select_option(entity_id="input_select.temperature_upstairs", option="Unoccupied")

@time_trigger("cron(0 17 * * *)")
def upstairs_evening_occupied():
    """Set Upstairs thermostat to Occupied at 5pm"""
    log.info("Setting Upstairs thermostat to Occupied (5pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_upstairs", option="Normal")

@time_trigger("cron(0 22 * * *)")
def upstairs_night_cold():
    """Set Upstairs thermostat to Cold at 10pm"""
    log.info("Setting Upstairs thermostat to Cold (10pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_upstairs", option="Cold")


# Schedule for Downstairs thermostat
@time_trigger("cron(0 6 * * *)")
def downstairs_morning_occupied():
    """Set Downstairs thermostat to Occupied at 6am"""
    log.info("Setting Downstairs thermostat to Occupied (6am schedule)")
    input_select.select_option(entity_id="input_select.temperature_downstairs", option="Normal")

@time_trigger("cron(0 22 * * *)")
def downstairs_night_unoccupied():
    """Set Downstairs thermostat to Unoccupied at 10pm"""
    log.info("Setting Downstairs thermostat to Unoccupied (10pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_downstairs", option="Unoccupied")


@time_trigger("cron(0 22 * * *)")
def office_night_off():
    """Set Office thermostat to Off at 10pm"""
    log.info("Setting Office thermostat to Off (10pm schedule)")
    input_select.select_option(entity_id="input_select.temperature_office", option="Off")
