import asyncio
import os

from dto import BaseWebSocketDTO, PLYUrlRequestDTO
from globals import get_client
from utils import get_last_ply_folder


async def run(
    building_id: str,
    ply_path: str,
    interval: float = 5.0,
):
    try:
        last_last_ply_folder = None
        while True:
            last_ply_folder = get_last_ply_folder(ply_path)

            if last_last_ply_folder != last_ply_folder:
                last_last_ply_folder = last_ply_folder
                last_ply = os.path.join(last_ply_folder, "point_cloud.ply")
                if os.path.exists(last_ply):
                    await get_client().get_session(
                        session_id=building_id
                    ).put_ply(last_ply)

                    await get_client().send(
                        BaseWebSocketDTO[PLYUrlRequestDTO](
                            data=PLYUrlRequestDTO(session_id=building_id)
                        )
                    )

            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("PLY task cancelled")
        raise
