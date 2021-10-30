import base64
import distutils
import os
import shlex
import subprocess
import sys
from typing import Dict, List, Optional, TextIO, Union

from click import Context
import docker


no_docker_message = (
    "Docker is not available on your system. "
    "Either install docker (https://docs.docker.com/install/), "
    "or run FreeSurfer/dcmqi commands locally (using the 'local' option)"
)

no_fs_license_message = (
    "Path to FreeSurfer License file is needed! "
    "Pass it with the --fs_license_key flag, "
    "or set the environment variable FS_LICENSE_KEY"
)


# basic defs
def check_for_docker() -> None:
    """Check if Docker is avalailable"""
    docker_available = distutils.spawn.find_executable("docker")
    if not docker_available:
        sys.exit(no_docker_message)


def check_requirements(context: Context) -> Context:
    """Check if requirements (Docker and FS license) are available

    Parameters
    ----------
    context : Context
        The Click Context used when running the hearth command

    Returns
    -------
    Context
        Click Context, updated with the base64 encoded FS_LICENSE_KEY if applicable
    """
    if context.obj["freesurfer_type"] == "docker":
        check_for_docker()
        if context.obj["fs_license_key"] is None:
            sys.exit(no_fs_license_message)
        else:
            fs_license_var = base64_convert(context.obj["fs_license_key"])
            context.obj["fs_license_var"] = fs_license_var

    if context.obj["dcmqi_type"] == "docker":
        check_for_docker()

    return context


def get_docker_user(file: TextIO) -> str:
    """Get UNIX user and group information, to use within Docker.

    This allows Hearth output to have the same user permissions as the user running the command,
    and same group permissions as the input file

    Parameters
    ----------
    file : TextIO
        Input file for command used within Docker

    Returns
    -------
    str
        UID:GID string, for use with docker run --user
    """
    uid = str(os.getuid())
    gid = str(os.stat(file).st_gid)

    return ":".join([uid, gid])


def run_docker_commands(
    docker_image: str,
    commands: List[str],
    volumes: Union[List[str], Dict[str, str]],
    user: str,
    environment: Optional[Union[List[str], Dict[str, str]]] = None,
    working_dir: str = os.getcwd(),
    pull: bool = True,
) -> None:
    """Run commands using Docker

    Parameters
    ----------
    docker_image : str
        Docker image name, including version (e.g. 'my_docker_image:v1.0')
    commands : list
        List of commands to run within `docker_image`
    volumes :  Union[List[str], Dict[str, str]]
        Volumes mounted within the `docker_image` when running
    user : str
        UID:GUI for UID of user running command, and the GID of input file
    environment : Optional[Union[List[str], Dict[str, str]]], optional
        Environment variables to set inside `docker_image` when running, by default None
    working_dir : str, optional
        Path to working director, by default os.getcwd()
    pull : bool, optional
        Pull `docker_image` before running, by default True
    """
    client = docker.from_env()

    if pull:
        client.images.pull(docker_image)
    for command in commands:
        print("[RunningCommand] {command}\n".format(command=command))
        container = client.containers.run(
            docker_image,
            command=shlex.split(command),
            volumes=volumes,
            environment=environment,
            user=user,
            working_dir=working_dir,
        )
        log = container.decode("utf-8")
        for i in log.split("\n"):
            print(i)
        print("--------")
    client.close()


def run_local_commands(commands: List[str]) -> None:
    """Run a list of commands

    Parameters
    ----------
    commands : List[str]
        List of command strings (e.g. ['ls -lrt', 'du -sh'])
    """
    for command in commands:
        subprocess.run(shlex.split(command))


def base64_convert(filename: Union[str, bytes, os.PathLike]) -> str:
    """Base64 encode a file

    This is used for passing the FS_KEY into the FreeSurfer docker container
    (like `docker run -e FS_KEY=...`).

    Same as
    base64 -w 1000 /path/to/fs_license

    Parameters
    ----------
    filename : str
        Path to FreeSurfer license file

    Returns
    -------
    str
        base64 encoded string of the FreeSurfer license
    """
    with open(filename, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode("ascii")

    return encoded_file


def abs_dirname(filename: Union[str, bytes, os.PathLike]) -> str:
    """Gets the absolute path of a directory containing a specific file

    Parameters
    ----------
    filename : Union[str, bytes, os.PathLike]
        The filename in question

    Returns
    -------
    str
        Absolute path to the directory containing the file
    """
    return os.path.dirname(os.path.abspath(os.path.expanduser(filename)))
