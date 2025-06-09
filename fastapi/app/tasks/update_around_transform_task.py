import asyncio
import math

from fastapi.logger import logger
from pyglm import glm

FPS = 20
ROTATION_SPEED = 60


async def run(around_client_id, around_session_id):
    from managers import unity_manager

    around_session = unity_manager.get_client(around_client_id).get_session(
        around_session_id
    )
    await around_session.wait_ready()
    try:
        angle_deg = 0.0
        radius = 30
        height = 10

        while True:
            angle_rad = math.radians(angle_deg)

            x = radius * math.cos(angle_rad)
            z = radius * math.sin(angle_rad)
            y = height
            position = glm.vec3(x, y, z)

            forward = glm.normalize(position - glm.vec3(0.0))
            up = glm.vec3(0, 1, 0)
            quat = glm.quatLookAt(forward, up)

            await around_session.set_camera_position(x, y, z)

            await around_session.set_camera_rotation(
                quat.x, quat.y, quat.z, quat.w
            )

            angle_deg = (angle_deg + ROTATION_SPEED / FPS) % 360
            await asyncio.sleep(1 / FPS)

    except asyncio.CancelledError:
        logger.info("Update around transform task cancelled")
        raise
