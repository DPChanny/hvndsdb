import asyncio
import math
from pyglm import glm

from fastapi.logger import logger

FPS = 20
ROTATION_SPEED = 60


async def run(center_client_id, center_session_id):
    from managers import unity_manager

    center_session = unity_manager.get_client(center_client_id).get_session(
        center_session_id
    )
    await center_session.wait_ready()
    try:
        angle_deg = 0.0

        while True:
            angle_rad = math.radians(angle_deg)
            quat = glm.angleAxis(angle_rad, glm.vec3(0, 1, 0))

            await center_session.set_camera_rotation(
                quat.x, quat.y, quat.z, quat.w
            )

            angle_deg = (angle_deg + ROTATION_SPEED / FPS) % 360
            await asyncio.sleep(1 / FPS)

    except asyncio.CancelledError:
        logger.info("Update center transform task cancelled")
        raise
