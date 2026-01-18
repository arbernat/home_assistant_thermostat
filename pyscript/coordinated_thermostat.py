@time_trigger("period(now, 15min)")
@state_trigger("climate.becky.current_temperature")
@state_trigger("climate.danny.current_temperature")
@state_trigger("climate.upstairs.current_temperature")
@state_trigger("climate.downstairs.current_temperature")
@state_trigger("climate.office")
@state_trigger("input_select.temperature_becky")
@state_trigger("input_select.temperature_danny")
@state_trigger("input_select.temperature_upstairs")
@state_trigger("input_select.temperature_downstairs")
def coordinated_thermostat_control():
    """
    Manage the thermostats for mini splits in our house.
    Three bedrooms (Becky, Danny, Upstairs)
    One large air handler (Downstairs)
    One office mini-split (Office)
    """
    
    # Temperature ranges for each thermostat based on their settings
    ranges = {
            "Warm": (72, 76),
            "Normal": (68, 72),
            "Cool": (65, 68),
            "Cold": (63, 65),
            "Unoccupied": (65, 76),
            "Off": (60, 80)
    }
    
    thermostats = {
        "becky": {
	        "entity": "climate.becky",
            "sensor": "sensor.thermometer_becky_temperature",
            "background": "input_text.thermostat_background_becky"
        },
        "danny": {
            "entity": "climate.danny",
            "sensor": "sensor.thermometer_danny_temperature",
            "background": "input_text.thermostat_background_danny"
        },
        "upstairs": {
            "entity": "climate.upstairs",
            "sensor": "sensor.thermometer_upstairs_temperature",
            "background": "input_text.thermostat_background_upstairs"
        },
        "downstairs": {
            "entity": "climate.downstairs",
            "sensor": "sensor.thermometer_downstairs_composite",
            "background": "input_text.thermostat_background_downstairs"
        },
        "office": {
            "entity": "climate.office",
            "sensor": None,
            "background": "input_text.thermostat_background_office"
        }
    }
    
    # Get current settings and temperatures
    thermostat_data = {}
    
    log.info("=== Thermostat Coordination Check ===")
    
    for name, data in thermostats.items():
        entity_id = data["entity"]
        sensor = data["sensor"]
        setting = state.get(f"input_select.temperature_{name}")
        current_temp_unit = float(state.getattr(entity_id).get("current_temperature", 70))
        if sensor:
            current_temp = float(state.get(sensor))
        else:
            current_temp = current_temp_unit
        min_temp, max_temp = ranges[setting]
        mid_temp = (min_temp + max_temp) / 2
        current_mode = state.get(entity_id)

        # Calculate delta from the acceptable range. 
        # If the unit is off use the appropriate boundary of the range (high or low)
        # If the unit is on use the midpoint of the range so we don't thrash at the
        # edge.
        log.info(f"{name} current mode is {current_mode}")
        
        if current_mode == "cool" and setting != "Off":
            target_max = mid_temp
        else:
            target_max = max_temp
        if current_mode == "heat" and setting != "Off":
            target_min = mid_temp
        else:
            target_min = min_temp
        if current_temp < target_min:
            delta = target_min - current_temp
            needs_mode = "heat"
        elif current_temp > target_max:
            delta = current_temp - target_max
            needs_mode = "cool"
        else:
            delta = 0
            needs_mode = "off"
            
        if delta > 4:
            fan_speed = "high"
        else:
            fan_speed = "auto"

        thermostat_data[name] = {
            "entity_id": entity_id,
            "current_temp": current_temp,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "mid_temp": mid_temp,
            "delta": delta,
            "needs_mode": needs_mode,
            "offset": current_temp_unit - current_temp,
            "fan_speed": fan_speed,
            "background": data["background"]
        }
        
        log.info(f"{name}: Setting={setting}, Temp={current_temp}°F, Range={min_temp}-{max_temp}°F, delta={delta:.1f}°F, Needs={needs_mode}, Unit Temp={current_temp_unit}, Fan Speed={fan_speed}")
    
    # Determine coordinated mode based on which thermostat is farthest from range
    max_heat_delta = 0
    max_cool_delta = 0
    
    for name, data in thermostat_data.items():
        if data["needs_mode"] == "heat":
            max_heat_delta = max(max_heat_delta, data["delta"])
        elif data["needs_mode"] == "cool":
            max_cool_delta = max(max_cool_delta, data["delta"])
    
    # Decide which mode wins:
    if max_heat_delta > max_cool_delta:
        coordinated_mode = "heat"
    elif max_cool_delta > max_heat_delta:
        coordinated_mode = "cool"
    else:
        coordinated_mode = "off"
    
    log.info(f"Max heat delta: {max_heat_delta:.1f}°F, Max cool delta: {max_cool_delta:.1f}°F")
    log.info(f"Desired mode: {coordinated_mode}")
    
    # Check if we can change modes (15 minute minimum runtime)
    last_mode_change = state.get("input_datetime.thermostat_last_mode_change")
    current_mode = state.get("input_text.thermostat_last_mode")
    
    if last_mode_change and last_mode_change not in ["unknown", "unavailable"]:
        import datetime
        last_change_time = datetime.datetime.fromisoformat(last_mode_change)
        now = datetime.datetime.now(last_change_time.tzinfo)
        minutes_elapsed = (now - last_change_time).total_seconds() / 60
        can_change = minutes_elapsed >= 15
    else:
        can_change = True
        
    mode_active = (coordinated_mode in ["heat", "cool"])
    same_mode = (coordinated_mode == current_mode)
    if mode_active and not same_mode and not can_change:
        coordinated_mode = current_mode

    did_change = False
    
    # Apply settings to each thermostat
    log.info("=== Applying Settings ===")
    for name, data in thermostat_data.items():
        entity_id = data["entity_id"]
        needed_mode = data["needs_mode"]
        allowed_mode = (needed_mode == coordinated_mode)
        
        # Determine if this thermostat should be active
        if coordinated_mode == "off":
            # All thermostats off if no one needs heating or cooling
            log.info(f"{name}: Setting to OFF (coordinated mode is off)")
            service.call("climate", "set_hvac_mode", 
                        entity_id=entity_id, 
                        hvac_mode="off")
            service.call("input_text", "set_value",
                        entity_id=data["background"],
                        value="off")
        elif allowed_mode:
            # This thermostat needs the active mode
            target_temp = data["mid_temp"] + data["offset"]
            log.info(f"{name}: Setting to {coordinated_mode.upper()} at {target_temp}°F (needs this mode)")
            service.call("climate", "set_hvac_mode", 
                        entity_id=entity_id, 
                        hvac_mode=coordinated_mode)
            service.call("climate", "set_temperature", 
                        entity_id=entity_id, 
                        temperature=target_temp)
            service.call("climate", "set_fan_mode",
                        entity_id=entity_id,
                        fan_mode=data["fan_speed"])
            service.call("input_text", "set_value",
                        entity_id=data["background"],
                        value=coordinated_mode)
            did_change = True
        elif data["delta"] == 0:
            # This thermostat is in range, turn it off
            log.info(f"{name}: Setting to OFF (in range)")
            service.call("climate", "set_hvac_mode", 
                        entity_id=entity_id, 
                        hvac_mode="off")
            service.call("input_text", "set_value",
                        entity_id=data["background"],
                        value="off")
        else:
            # This thermostat needs a different mode, turn it off
            log.info(f"{name}: Setting to OFF (needs {data['needs_mode']} but coordinated mode is {coordinated_mode})")
            service.call("climate", "set_hvac_mode", 
                        entity_id=entity_id, 
                        hvac_mode="off")
            service.call("input_text", "set_value",
                        entity_id=data["background"],
                        value="conflict")    
    if did_change:
        service.call("input_datetime", "set_datetime", 
            entity_id="input_datetime.thermostat_last_mode_change",
            timestamp=task.executor(lambda: __import__('time').time()))
        service.call("input_text", "set_value",
            entity_id="input_text.thermostat_last_mode",
            value=coordinated_mode)
            
    
    log.info("=== Coordination Complete ===")


