# home_assistant_thermostat
A Home Assistant thermostat configuration for multiple mini-splits.

My house has the following configuration:
* A single heat pump condenser unit (Mitsubishi)
* Four mini splits; three in bedrooms and one in an office.
* A single air handler that conditions the downstairs.

And family requirements:
* My daughter (Becky) likes to sleep with her room cold, so it needs to cool down at bedtime.
* My son (Danny) likes his room warm.
* The upstairs bedroom should similarly cool down at night.
* Rooms are vacant during the day (kids are in school) so we can avoid conditioning them.
* The office is empty most of the time so should not be conditioned except when required.
* We want to let the downstairs go unconditioned at night to save money.

This posed some difficulties to getting a running system. In rough chronological order:
* First attempt: Mitsubishi remotes and hand-coded schedules. This frequently failed with collisions between the mini splits; one would block all others. 
* Second attempt: Cielo Wiegle brand thermostats. These promised coordination but also had two failure modes. Their "comfy" and coordination capabilities do not work well together, resulting in rooms spiking to very hot or cold temperatures. They also do not coordinate beween the minisplit thermostats and their conventional thermostat line.
* Third attempt: Home Assistant + ESP32 as described here. So far this is working.

Requirements:
* Home Assistant. I have a Home Assistant Green; I don't think that's a hard requirement.
* Pyscript installed on HA. The main scripts are written in Python, not native YAML.
* ESP32 controls for the Mitsubishi thermostats. I used the instructions here: https://jhthompson12.github.io/2025-01-27-MiniSplit-Controller/ with some additional steps (noted below)
* (Optional) Apple Homekit. We are an Apple household so I added the ability to control the temperature via Homekit integrations.

# Theory of Operation

The user input to the algorithm is a set of (room, desired temperature) pairs. The rooms are [Upstairs, Danny, Becky, Downstairs, Office], corresponding to minisplits or air handlers. The desired temperature comes from a list [Warm, Normal, Cool, Cold, Unoccupied, Off]. The temperatures correspond to ranges; warm is 72-75F, normal is 68-72F, cool is 65-68F, and cold is 63-65F. Unoccupied is a range from 65-75. Off is a range from 60-80 but also has some special handling.

The system input to the algorithm are temperatures from the following sources:
* Zigbee thermometers in all the bedrooms. I used these: https://3reality.com/product/temperature-and-humidity-sensor-lite/
* Zigbee thermometers in the major downstairs room, averaging to a single "downstairs temperature".
* The built-in thermometer in the office. This is wildly inaccurate unless the unit is running but since it stays off most of the time that's fine.

Every time tick (every 15 minutes or when initiated by Home Assistant) the following algorithm runs:

* For each room, calculate the desired temperature range and the current temperature. If the current temperature is in the range, record a desired state of "off". If not, record "heat" or "cool" as appropriate.
* See if the heat pump has been running for more than 15 minutes. If it hasn't, do not allow it to switch modes.
* Identify the room with the highest delta between desired and current temperature. This sets the master mode of heat/cool. If this conflicts with step 2, override the master mode to the current mode.
* For each room, identify if the minisplit should be on (matching the master mode), off, or in conflict. Minisplits in conflict record that state for the UI and then turn off.
* Apply the desired state to all units.
* Record the state of all units for the UI

There is one wrinkle: the downstairs air handler uses an internal thermometer that is not accurate. Also calculate the delta beween what the in-room thermometers believe the temperature is and what the unit says; adjust the set point by this much to compensate.

# ESP32 Configuration

The ESP32 configuration consists of the files in esp32/. There is a shared "AC.yaml" and five individual configuration files. For the minisplits the remote temperature is injected into the unit. This doesn't consistently work for the downstairs air handler (I think it's being overridden again by the unit), hence the workaround.

I used ESP32 boards are described above (https://jhthompson12.github.io/2025-01-27-MiniSplit-Controller/). To initially flash the boards I plugged them into the Home Assistant Green (not my laptop). I then held both buttons (reset and 0), released reset, and released 0. This let me flash the initial image. Since then flashing via WiFi has been fine. As you can see in the files I use static IPs for each ESP32.

# Home Assistant Configuration

This is the big one. There are multiple categories of sensors, climate entities, and helpers.

* Climate: The ESP32 widgets are named [climate.becky, climate.danny, climate.downstairs, climate.office, climate.upstairs]
* Sensors: The 3rd reality thermometers expose the following sensors:
  * Thermometers: sensor.thermometer_becky_temperature, sensor.thermometer_danny_temperature, sensor.thermometer_upstairs_temperature. There are also three downstairs (same naming pattern, Library, Living Room, and Kitchen)
  * Humidity: sensor.thermometer_becky_humidity, etc.
* An averaged sensor.thermometer_downstairs_composite. This is implemented as a "combine the state of several sensors" helper. Similarly for humidity.
* Dropdowns for the desired temperature of each room. The set is as described above [Warm, Normal, Cool, Cold, Unoccupied, Off]. The naming scheme is input_select.temperature_<room>; e.g. input_select.temperature_becky
* Input text fields to record the mode of each thermostat for the interface. These are named "input_text.thermostat_background_<room>", e.g. input_text.thermostat_background_becky
* Input text for the previous mode of the heat pump named "input_text.thermostat_last_mode". Used to detect conflicts.
* Input datetime for the last mode change. Named "input_datetime.thermostat_last_mode_change"

# Dashboard configuration

After all that the dashboard is relatively straightforward. It is one tab of a dedicated Home Assistant iOS app on an iPad in the kitchen. The dashboard is also accessible via a browser. Most of the time it's set it and forget it though.

# HACS
I have so many HACS repositories. The ones in play here are:
* mini-graph-card
* card-mod
* layout-card
* pyscript
* Mushroom
* Decluttering Card
* Simple Tabs Card
* Text Divider Row
* Weather Card Extended
* 
