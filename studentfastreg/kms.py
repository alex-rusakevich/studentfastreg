from logging import getLogger

import requests

from studentfastreg.settings import KMS_SERVER, PROGRAM_NAME

logger = getLogger(__name__)


def is_org_act(org_name: str) -> bool:
    if org_name == "Тестовая организация":
        return True
    else:
        kms_server = KMS_SERVER + "/api/kms/is_activated"

        logger.debug("Sending request to " + kms_server + "...")

        resp = requests.post(
            kms_server,
            json={"product_name": PROGRAM_NAME, "org_name": org_name},
        )

        if resp.status_code != 200:
            logger.exception("Bad server response: " + str(resp.content))
            return False

        is_activated = resp.json()["is_activated"]

        logger.info(f"Activation status: {is_activated}")

        return resp.json()["is_activated"]
