"""Provides the 4heatlite DataUpdateCoordinator."""
from datetime import timedelta
import json
import logging
import socket
import time

from async_timeout import timeout
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SOCKET_BUFFER,
    SOCKET_TIMEOUT,
    TCP_PORT,
    DATA_QUERY,
    ON_CMD,
    OFF_CMD,
    UNBLOCK_CMD,
    RESULT_DATA,
    RESULT_ERROR,
    MODE_STATE_BYTE_OFFSET,
    MODE_NAMES,
)

_LOGGER = logging.getLogger(__name__)

# Le module 4heatlite ne semble accepter qu'une connexion TCP a la fois et
# refuse (ConnectionRefusedError) toute tentative pendant qu'il en traite
# deja une autre (ex: appli officielle ouverte en meme temps, ou connexion
# precedente pas encore liberee cote module). On tente donc plusieurs fois
# avant d'abandonner.
CONNECT_RETRIES = 3
CONNECT_RETRY_DELAY = 2.0  # secondes


def _send_and_receive(
    host: str, payload: list, retries: int = CONNECT_RETRIES, retry_delay: float = CONNECT_RETRY_DELAY
) -> list:
    """Envoie une commande JSON (liste) au module 4heatlite et renvoie la reponse parsee.

    IMPORTANT : separators=(",", ":") est obligatoire, le parseur du module
    est strict et rejette (["ERR","1","1"]) toute trame contenant un espace.

    Reessaie automatiquement en cas de connexion refusee/timeout, avec une
    courte pause entre les tentatives (fonction reutilisee telle quelle par
    config_flow.py pour le test de connexion initial).
    """
    data = json.dumps(payload, separators=(",", ":")).encode()
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(SOCKET_TIMEOUT)
        try:
            s.connect((host, TCP_PORT))
            s.send(data)
            raw = s.recv(SOCKET_BUFFER).decode()
            _LOGGER.debug("Commande envoyee: %s", data)
            _LOGGER.debug("Reponse brute: %s", raw)
            return json.loads(raw)
        except (ConnectionRefusedError, OSError, socket.timeout) as ex:
            last_error = ex
            _LOGGER.warning(
                "Connexion au module 4heatlite echouee (tentative %s/%s): %s",
                attempt,
                retries,
                ex,
            )
            if attempt < retries:
                time.sleep(retry_delay)
        finally:
            s.close()

    raise last_error


class FourHeatDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching 4heatlite data."""

    def __init__(self, hass: HomeAssistant, *, config: dict, options: dict, id: str):
        """Initialize global 4heatlite data updater."""
        self._host = config[CONF_HOST]
        self.stove_id = id
        self.model = "4heatlite"
        self.serial_number = "1"
        # trames hex brutes du dernier "2WL", indexees par id de parametre
        # (ex: "005a" -> "12005a00dc006401900001000100000000")
        # necessaires pour reconstruire une commande d'ecriture (bornes min/max
        # a recopier telles quelles).
        self._last_frames: dict[str, str] = {}

        update_interval = timedelta(seconds=20)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the stove (requete 2WL)."""

        def _update_data() -> dict:
            data = self.data or {}
            response = _send_and_receive(self._host, DATA_QUERY)

            if not response:
                raise UpdateFailed("Reponse vide du module")

            if response[0] == RESULT_ERROR:
                raise UpdateFailed("Le module a renvoye une erreur ERR")

            if response[0] != RESULT_DATA:
                raise UpdateFailed(f"Reponse inattendue: {response[0]}")

            frames = response[2:]  # response[0]=tag "2WL", response[1]=nb de trames

            for frame_hex in frames:
                frame = bytes.fromhex(frame_hex)

                if frame[0] == 0x10:
                    # Trame d'entete "MAINVALUES" : porte le code d'etat du poele
                    mode_code = frame[MODE_STATE_BYTE_OFFSET]
                    data["mode"] = MODE_NAMES.get(mode_code, f"Unknown ({mode_code})")
                    data["mode_code"] = mode_code
                    continue

                if frame[0] in (0x12, 0x0E) and len(frame) >= 5:
                    param_id = frame[1:3].hex()
                    value = int.from_bytes(frame[3:5], "big")
                    data[param_id] = value
                    self._last_frames[param_id] = frame_hex

            return data

        try:
            async with timeout(10):
                return await self.hass.async_add_executor_job(_update_data)
        except UpdateFailed:
            raise
        except Exception as error:
            raise UpdateFailed(f"Invalid response from stove: {error}") from error

    async def async_turn_on(self) -> bool:
        try:
            await self.hass.async_add_executor_job(_send_and_receive, self._host, ON_CMD)
            _LOGGER.debug("Commande marche envoyee")
        except Exception as ex:
            _LOGGER.error(ex)

    async def async_turn_off(self) -> bool:
        try:
            await self.hass.async_add_executor_job(_send_and_receive, self._host, OFF_CMD)
            _LOGGER.debug("Commande arret envoyee")
        except Exception as ex:
            _LOGGER.error(ex)

    async def async_unblock(self) -> bool:
        try:
            await self.hass.async_add_executor_job(_send_and_receive, self._host, UNBLOCK_CMD)
            _LOGGER.debug("Commande deblocage envoyee")
        except Exception as ex:
            _LOGGER.error(ex)

    async def async_set_temperature(self, param_id: str, temperature: float) -> bool:
        """Change une consigne de temperature (parametre type 0x12, ex PARAM_ROOM_SETPOINT = '005a').

        Reprend la derniere trame lue pour ce parametre afin de conserver les
        bornes min/max, comme fait l'appli officielle (fonction aggiornacomando2w).
        """
        current_frame_hex = self._last_frames.get(param_id)
        if current_frame_hex is None:
            _LOGGER.error(
                "Trame actuelle inconnue pour le parametre %s : "
                "attendez une premiere mise a jour (2WL) avant d'ecrire",
                param_id,
            )
            return False

        valeur = round(temperature * 10)
        if valeur < 0:
            valeur += 65536
        v_hex = format(valeur, "x")
        if len(v_hex) == 2:
            v_hex = "00" + v_hex
        elif len(v_hex) == 3:
            v_hex = "0" + v_hex

        comando = "05" + current_frame_hex[0:6] + v_hex + current_frame_hex[10:28]
        payload = ["2WC", "1", comando]

        try:
            await self.hass.async_add_executor_job(_send_and_receive, self._host, payload)
            _LOGGER.debug("Consigne du parametre %s mise a %.1f C", param_id, temperature)
            return True
        except Exception as ex:
            _LOGGER.error(ex)
            return False
