import asyncio
import os
import subprocess

from dto import BaseWebSocketDTO, CompleteDTO
from globals import get_client
from utils import get_last_checkpoint

ITERATION = 5000
SAVE_CHECKPOINT_INTERVAL = 25


async def run(
        session_id: str,
        colmap_path: str,
        frames_path: str,
        posenet_path: str,
        iteration: int = ITERATION,
):
    loop = asyncio.get_running_loop()
    process = None
    try:
        if not os.path.isdir(posenet_path):
            os.mkdir(posenet_path)

        cmd = [
            "python",
            "-u",
            "-m",
            "posenet.train",
            "--images_txt_path",
            os.path.join(colmap_path, "sparse", "0", "txts", "images.txt"),
            "--output_path",
            posenet_path,
            "--frames_root",
            frames_path,
        ]

        start_checkpoint = get_last_checkpoint(posenet_path)
        if start_checkpoint is not None:
            cmd += [
                "--checkpoint_path",
                os.path.join(posenet_path, f"chkpnt{start_checkpoint}.pth"),
                "--resume",
            ]

        start_checkpoint = (
            start_checkpoint if start_checkpoint is not None else 0
        )

        cmd += [
            "--epochs",
            str(start_checkpoint + iteration),
        ]

        cmd += [
            "--save_checkpoints",
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

        last_checkpoint = get_last_checkpoint(posenet_path)
        if last_checkpoint:
            session.load_model(
                os.path.join(posenet_path, f"chkpnt{last_checkpoint}.pth")
            )

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
