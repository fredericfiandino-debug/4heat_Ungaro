"""Constantes pour l'intégration 4heatlite (Ungara Fagiolo / Tiemme, protocole "2ways" 2WL/2WC).

Ce fichier ne contient QUE les éléments validés en conditions réelles avec le
module 4heatlite (192.168.1.72:80, HTTP brut, JSON compact sans espaces).
Il ne réutilise pas les codes de l'ancien protocole ASCII "SEC"/"SEL" (autre
génération de module, non compatible).
"""
from datetime import timedelta

from homeassistant.const import UnitOfTemperature

DOMAIN = "4heatlite"
DATA_COORDINATOR = "coordinator"

ATTR_STOVE_ID = "stove_id"
ATTR_READING_ID = "reading_id"

# --- Connexion TCP ---
TCP_PORT = 80
SOCKET_BUFFER = 8192
SOCKET_TIMEOUT = 10
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=20)

# --- Requête / commandes ---
# IMPORTANT : le module a un parseur JSON strict. Toujours sérialiser avec
# json.dumps(payload, separators=(",", ":")) pour ne PAS avoir d'espaces,
# sinon le module répond ["ERR","1","1"].
DATA_QUERY = ["2WL", "0"]

ON_CMD = ["2WC", "1", "05040000"]
OFF_CMD = ["2WC", "1", "05050000"]
UNBLOCK_CMD = ["2WC", "1", "05050000"]  # même trame que OFF_CMD

RESULT_DATA = "2WL"
RESULT_CMD_ACK = "2WC"
RESULT_ERROR = "ERR"

# --- Paramètres type 0x12 (trame de 17 octets, valeur sur 2 octets à l'offset 3) ---
# Températures en dixièmes de degré Celsius (diviseur 10).
PARAM_EXHAUST_TEMP = "ffff"  # Température fumées
PARAM_ROOM_TEMP = "fff7"  # Température ambiante
PARAM_ROOM_TEMP_REMOTE_1 = "ffe0"  # Température ambiante à distance 1 (sonde absente ici)
PARAM_ROOM_TEMP_REMOTE_2 = "ffe8"  # Température ambiante à distance 2 (sonde absente ici)
PARAM_AIR_FLOW = "ffed"  # Flux d'air (%)
PARAM_BUFFER_THERMOSTAT = "ffdf"  # Thermostat ballon / SERVICE 4WEB
PARAM_CLEANING = "ffde"  # CLEANING 4WEB
PARAM_ROOM_SETPOINT = "005a"  # Consigne thermostat ambiance (lecture + écriture confirmées)
PARAM_ROOM_SETPOINT_REMOTE_1 = "0058"
PARAM_ROOM_SETPOINT_REMOTE_2 = "0059"

# --- Paramètres type 0x0e (trame de 17 octets, valeur entière sur 2 octets à l'offset 3) ---
PARAM_COMBUSTION_POWER = "016c"  # Puissance de combustion
PARAM_HEATING_POWER = "023f"  # Puissance de chauffage / diffusion
PARAM_CANALIZED_POWER_1 = "0266"  # Puissance canalisée 1
PARAM_CANALIZED_POWER_2 = "027e"  # Puissance canalisée 2
PARAM_SELECTOR = "0231"  # Sélecteur Local / Remote / Local-Remote

# [id de paramètre] -> [nom, unité, icône, device_class, state_class, diviseur]
# Note : PARAM_ROOM_SETPOINT n'est plus ici — c'est une entité "number"
# (réglable) dans number.py, pas un simple capteur en lecture seule.
SENSOR_TYPES = {
    PARAM_EXHAUST_TEMP: ["Température fumées", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement", 10],
    PARAM_ROOM_TEMP: ["Température ambiante", UnitOfTemperature.CELSIUS, "mdi:thermometer", "temperature", "measurement", 10],
    PARAM_COMBUSTION_POWER: ["Puissance de combustion", None, "mdi:fire", None, None, 1],
    PARAM_HEATING_POWER: ["Puissance de chauffage", None, "mdi:fan", None, None, 1],
    PARAM_CANALIZED_POWER_1: ["Puissance canalisée 1", None, "mdi:fan", None, None, 1],
    PARAM_CANALIZED_POWER_2: ["Puissance canalisée 2", None, "mdi:fan", None, None, 1],
    PARAM_SELECTOR: ["Sélecteur", None, "mdi:remote", None, None, 1],
    PARAM_AIR_FLOW: ["Flux d'air", "%", "mdi:air-filter", None, None, 1],
}

# Niveaux de puissance (P1..P6, ou 7="Auto") — table issue de l'ancien
# protocole, reprise telle quelle car le format de valeur (1-7) est le même.
POWER_NAMES = {
    1: "P1",
    2: "P2",
    3: "P3",
    4: "P4",
    5: "P5",
    6: "P6",
    7: "Auto",
}

# Codes d'erreur — NON TESTÉS chez vous, repris de l'ancien protocole tel
# quel. On ne sait pas encore quel octet/trame porte ce code sur le
# 4heatlite (piste : octet 2 de la trame "0c81...", jamais vu bouger de 0
# pour l'instant) : ne pas câbler d'entité dessus tant que ce n'est pas
# confirmé par un test réel (ex: déclencher une erreur volontairement).
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

# Paramètres dont la valeur brute doit être traduite via une table plutôt
# que divisée numériquement (les 4 puissances -> "P1".."P6"/"Auto").
PARAM_VALUE_MAPS = {
    PARAM_COMBUSTION_POWER: POWER_NAMES,
    PARAM_HEATING_POWER: POWER_NAMES,
    PARAM_CANALIZED_POWER_1: POWER_NAMES,
    PARAM_CANALIZED_POWER_2: POWER_NAMES,
}


# --- État du poêle ---
# Porté par l'octet 5 de la trame d'en-tête "10..." (frame "MAINVALUES").
# Table issue du FileMap officiel du poêle (lingue_stati).
# Entrées marquées "testé" confirmées en conditions réelles (cycle marche/arrêt) ;
# les autres proviennent du FileMap mais n'ont pas encore été observées.
MODE_STATE_BYTE_OFFSET = 5  # offset dans la trame "10..." décodée en octets

MODE_NAMES = {
    0: "Off",  # SPENTO — testé
    1: "Check Up",  # CHECK UP — testé (juste après commande marche)
    2: "Ignition",  # ACCENSIONE
    3: "Stabilization",  # STABILIZZAZIONE
    4: "Retry Ignition",  # RITENTA
    5: "Run",  # NORMALE
    6: "Modulation",  # MODULAZIONE
    7: "Extinguishing",  # SPEGNIMENTO — testé (juste après commande arrêt)
    8: "Safety",  # SICUREZZA
    9: "Block",  # BLOCCO
    10: "Recover Ignition",  # RECUPERO ACCENSIONE
    11: "Standby",  # STANDBY
}
