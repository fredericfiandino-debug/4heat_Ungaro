"""Constants for the 4Heat integration."""
from datetime import timedelta

from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfVolumeFlowRate,
)

DOMAIN = "4heat"

ATTR_STOVE_ID = "stove_id"
ATTR_READING_ID = "reading_id"
ATTR_MARKER = "marker"
ATTR_NUM_VAL = "num_val"

DATA_QUERY = b'["2WL","0"]'
ERROR_QUERY = b'["SEC","3","I30001000000000000","I30002000000000000","I30017000000000000"]'
UNBLOCK_CMD = b'["2WC","1","05050000"]' # Unblock (same command used as for OFF_CMD)
OFF_CMD = b'["2WC","1","05050000"]' # OFF
ON_CMD = b'["2WC","1","05040000"]' # ON

OFF_CMD_OLD = b'["2WL","0"]' # OFF
ON_CMD_OLD = b'["2WC","1","05040000"]' # ON

MODES = [[ON_CMD, OFF_CMD, UNBLOCK_CMD], [ON_CMD_OLD, OFF_CMD_OLD, None]]
CONF_MODE = 'mode'
CMD_MODE_OPTIONS = ['Full set (default)', 'Limited set']

RESULT_VALS = 'SEC'
RESULT_ERROR = 'ERR'

TCP_PORT = 80

SOCKET_BUFFER = 1024
SOCKET_TIMEOUT = 10

DATA_COORDINATOR = "corrdinator"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=20)

MODE_TYPE = "c8101"
ERROR_TYPE = "30002"
POWER_TYPE = "20364"

SENSOR_TYPES = {
    "c8101": ["State", None, "", None, None],
    "30002": ["Error", None, "", None, None],
    "30003": ["Timer", None, "", None, None],
    "30004": ["Ignition", None, "", None, None],
    "2ffff": ["Exhaust temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "30006": ["Room temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "30007": ["Inputs", None, "", None, None],
    "30008": ["Combustion fan", None, "", None, None], #RPM
    "30009": ["Heating fan", None, "", None, None],
    "30011": ["Combustion power", None, "", None, None],
    "2fffa": ["Buffer temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "30015": ["UN 30015", None, "", None, None],
    "2fffc": ["Boiler water", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "2fffb": ["Water pressure", UnitOfPressure.MBAR, "", None, None],
    "30025": ["Comb.FanRealSpeed", None, "", None, None],
    "30026": ["Airstream", UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR, "", None, None],
    "30033": ["Exhaust depression", UnitOfPressure.PA, "", None, None],
    "30040": ["UN 30040", None, "", None, None],
    "30044": ["UN 30044", None, "", None, None],
    "30084": ["Water pump", None, "", None, None],
    "40007": ["UN 40007", None, "", None, None],
    "20005": ["Min Range of Buffer Thermostat", None, "", None, None],
    "2ffe2": ["Max Range of Buffer Thermostat", None, "", None, None],
    "20180": ["Buffer target", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "20199": ["Buffer target", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "e00e1": ["Min Temp of Buffer", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "e00c7": ["Set Temp of Buffer", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "20211": ["UN 20211", None, "", None, None],
    "20225": ["UN 20225", None, "", None, None],
    "20364": ["Power Setting", None, None, None],
    "20381": ["UN 20381", None, "", None, None],
    "20365": ["UN 20365", None, "", None, None],
    "20366": ["UN 20366", None, "", None, None],
    "20369": ["UN 20369", None, "", None, None],
    "20374": ["UN 20374", None, "", None, None],
    "20385": ["UN 20385", None, "", None, None],
    "20375": ["UN 20375", None, "", None, None],
    "20575": ["UN 20575", None, "", None, None],
    "20493": ["Room temperature set point", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "20570": ["UN 20570", None, "", None, None],
    "20801": ["Heating power", None, None, None],
    "20803": ["UN 20803", None, "", None, None],
    "20813": ["UN 20813", None, "", None, None],
    "21700": ["Room termostat", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement"],
    "40016": ["Outputs", None, "", None, None],
    "50001": ["Auger on", None, "", None, None],
}

MODE_NAMES = {
    256: "Ignition",
    1: "Check Up",
    2: "Ignition",
    3: "Stabilization",
    4: "Ignition",
    512: "Run",
    1024: "Run",
    1280: "Run",
    6: "Modulation",
    7: "Extinguishing",
    8: "Safety",
    0: "Off",
    10: "RecoverIgnition",
    11: "Standby",
    48: "Ignition",
    51: "Ignition",
    52: "Ignition",
}

ERROR_NAMES = {
    0: "No",
    1: "Safety Thermostat HV1: signalled also in case of Stove OFF",
    2: "Safety PressureSwitch HV2: signalled with Combustion Fan ON",
    3: "Extinguishing for Exhausting Temperature lowering",
    4: "Extinguishing for water over Temperature",
    5: "Extinguishing for Exhausting over Temperature",
    6: "unknown",
    7: "Encoder Error: No Encoder Signal (in case of P25=1 or 2)",
    8: "Encoder Error: Combustion Fan regulation failed (in case of P25=1 or 2)",
    9: "Low pressure in to the Boiler",
    10: "High pressure in to the Boiler Error",
    11: "DAY and TIME not correct due to prolonged absence of Power Supply",
    12: "Failed Ignition",
    13: "Ignition",
    14: "Ignition",
    15: "Lack of Voltage Supply",
    16: "Ignition",
    17: "Ignition",
    18: "Lack of Voltage Supply",
}

POWER_NAMES = {
    1: "P1",
    2: "P2",
    3: "P3",
    4: "P4",
    5: "P5",
    6: "P6",
    7: "Auto",
}
