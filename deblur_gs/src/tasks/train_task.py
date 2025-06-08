import asyncio
import os
import subprocess

from dto import BaseWebSocketDTO, CompleteDTO
from envs import VISDOM_HOST, VISDOM_PORT
from globals import get_client
from utils import get_last_checkpoint

ITERATION = 5000
SAVE_POINT_CLOUD_INTERVAL = 50
SAVE_CHECKPOINT_INTERVAL = 500


async def run(
    session_id: str,
    colmap_path: str,
    frames_path: str,
    deblur_gs_path: str,
    iteration: int = ITERATION,
):
    loop = asyncio.get_running_loop()
    process = None
    try:
        cmd = [
            "python",
            "-u",
            "-m",
            "deblur_gs.train",
            "-s",
            colmap_path,
            "-m",
            deblur_gs_path,
            "-i",
            frames_path,
            "--test_iterations",
            "-1",
            "--deblur",
            "--visdom_server",
            VISDOM_HOST,
            "--visdom_port",
            str(VISDOM_PORT),
        ]

        start_checkpoint = get_last_checkpoint(deblur_gs_path)
        if start_checkpoint is not None:
            cmd += [
                "--start_checkpoint",
                os.path.join(deblur_gs_path, f"chkpnt{start_checkpoint}.pth"),
            ]

        start_checkpoint = (
            start_checkpoint if start_checkpoint is not None else 0
        )

        cmd += [
            "--iterations",
            str(start_checkpoint + iteration),
        ]

        cmd += [
            "--save_iterations",
            *[
                str(i)
                for i in range(
                    start_checkpoint,
                    start_checkpoint + iteration + 1,
                    SAVE_POINT_CLOUD_INTERVAL,
                )
            ],
        ]

        cmd += [
            "--checkpoint_iterations",
            *[
                str(i)
                for i in range(
                    start_checkpoint,
                    start_checkpoint + iteration + 1,
                    SAVE_CHECKPOINT_INTERVAL,
                )
            ],
        ]

        session = get_client().get_session(session_id)
        await session.update_progress(" ".join(cmd))

        def process():
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

        process = await loop.run_in_executor(None, process)
        while process.poll() is None:
            line = await loop.run_in_executor(None, process.stdout.readline)
            line = line.strip()
            await session.update_progress(line)

        await get_client().send(
            BaseWebSocketDTO[CompleteDTO](
                data=CompleteDTO(session_id=session_id)
            )
        )
    except asyncio.CancelledError:
        print("Train worker cancelled")
        if process and process.poll() is None:
            process.kill()
            await loop.run_in_executor(None, process.wait)
        raise
    except Exception as e:
        print(e)

    print("Train worker finished")
