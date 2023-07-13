import json
from asyncio import iscoroutinefunction, subprocess
from io import BytesIO
from typing import Any

from aiopath import AsyncPath

from tgtools.utils.types import FileOrPath, FilePath


async def seek(file: Any, offset: int) -> None:
    if seek := getattr(file, "seek"):
        if iscoroutinefunction(seek):
            await seek(offset)
        else:
            seek(offset)


async def ffmpeg(input: bytes, *arguments: str) -> BytesIO | None:
    """
    Run an ffmpeg command

    Args:
        input (bytes): Input file data
        *arguments (list[str]): Parameters for ffmpeg command

    Returns:
        The new file as BytesIO or None if it failed
    """
    input_file = "-i", "pipe:0"

    process = await subprocess.create_subprocess_exec(
        "ffmpeg",
        "-y",
        *input_file,
        *arguments,
        "pipe:1",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    stdout, _ = await process.communicate(input)
    return BytesIO(stdout) if stdout else None


async def ffprobe(input: bytes, *arguments: str) -> dict[str, Any]:
    """
    Run an ffprobe command

    Args:
        input (bytes): Input file data
        *arguments (list[str]): Parameters for ffmpeg command

    Returns:
        The info returned as JSON
    """
    output_format = "-of", "json"

    process = await subprocess.create_subprocess_exec(
        "ffprobe",
        *arguments,
        *output_format,
        "-",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    try:
        stdout, _ = await process.communicate(input)
    except BrokenPipeError:
        pass

    return json.loads(stdout) if stdout else None  # type: ignore[no-any-return ]


async def read_file_like(file: FileOrPath) -> bytes:
    """
    Read and return bytes from file like or file path
    """
    await seek(file=file, offset=0)
    if isinstance(file, FilePath):  # type: ignore[arg-type, misc]
        content = await AsyncPath(file).read_bytes()
    elif isinstance(file, BytesIO):
        content = file.getvalue()
    elif (read := getattr(file, "read", None)) and iscoroutinefunction(read):
        content = await read()
    else:
        content = file.read()  # type: ignore[union-attr]
    await seek(file=file, offset=0)
    return content  # type: ignore[no-any-return]
