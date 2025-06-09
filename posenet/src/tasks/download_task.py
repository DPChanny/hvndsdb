import asyncio
import os.path
from typing import Optional


async def run(
    session_id: str,
    frames_url: str,
    colmap_url: str,
    posenet_url: Optional[str] = None,
):
    from envs import TEMP
    from dto import BaseSessionReadyDTO, BaseWebSocketDTO
    import subprocess

    loop = asyncio.get_running_loop()

    cmd = [
        "python",
        "-u",
        __file__,
        session_id,
        TEMP,
        frames_url,
        colmap_url,
    ]
    if posenet_url:
        cmd.append(posenet_url)

    def process():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    process = await loop.run_in_executor(None, process)
    from globals import get_client

    session = get_client().get_session(session_id)

    while process.poll() is None:
        line = await loop.run_in_executor(None, process.stdout.readline)
        line = line.strip()
        await session.update_progress(line)

    from utils import get_last_checkpoint

    try:
        last_checkpoint = get_last_checkpoint(
            os.path.join(TEMP, session_id, "posenet")
        )
        if last_checkpoint:
            session.load_model(
                os.path.join(
                    TEMP, session_id, "posenet", f"chkpnt{last_checkpoint}.pth"
                )
            )
    except Exception as e:
        print(e)

    await get_client().send(
        BaseWebSocketDTO[BaseSessionReadyDTO](
            data=BaseSessionReadyDTO(session_id=session_id)
        )
    )

    print(f"Download task finished")


async def main():
    import os
    import sys

    from downloader import download_folder_from_presigned_url

    session_id = sys.argv[1]
    temp = sys.argv[2]
    frames_url = sys.argv[3]
    colmap_url = sys.argv[4]
    posenet_url = sys.argv[5] if len(sys.argv) > 5 else None

    session_path = os.path.join(temp, session_id)

    await download_folder_from_presigned_url(
        frames_url, os.path.join(session_path, "frames"), temp
    )
    await download_folder_from_presigned_url(
        colmap_url, os.path.join(session_path, "colmap"), temp
    )

    if posenet_url:
        await download_folder_from_presigned_url(
            posenet_url, os.path.join(session_path, "posenet"), temp
        )


if __name__ == "__main__":
    asyncio.run(main())
