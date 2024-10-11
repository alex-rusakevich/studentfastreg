import os
import platform
from io import StringIO

from invoke import run, task


@task
def clear(context):
    os.system("rm -rf build/*.*")
    os.system("rm -rf dist/*.*")
    os.system("rm -f *.spec")


@task
def build(context, folder_mode=False):
    STUDENTFASTREG_VERSION = (
        open(os.path.join("studentfastreg", "VERSION.txt"), "r", encoding="utf8")
        .read()
        .strip()
    )

    OS_NAME = platform.system().lower()

    run(
        f'pyinstaller \
--name=studentfastreg-v{STUDENTFASTREG_VERSION}-{OS_NAME} \
--noconfirm {"--onefile" if not folder_mode else ""} --windowed \
--icon "./resources/icons/favicon.ico" \
--add-data "./resources:resources/" \
--add-data "./studentfastreg/VERSION.txt:studentfastreg/" \
"./studentfastreg.py"'
    )


@task
def req(context):
    run("pipenv install")
    run("pipenv install --dev")


@task
def start(context):
    run("pipenv run python studentfastreg.py")


@task
def designer(context):
    run("qt6-tools designer")


@task
def update_version_txt(context):
    STUDENTFASTREG_VERSION = (
        open(os.path.join("studentfastreg", "VERSION.txt"), "r", encoding="utf8")
        .read()
        .strip()
    )

    latest_commit_msg = StringIO()
    run("git log -1 --pretty=%B", out_stream=latest_commit_msg)
    latest_commit_msg = latest_commit_msg.getvalue().strip()

    major, minor, patch = (int(i) for i in STUDENTFASTREG_VERSION.split("."))

    if "#patch" in latest_commit_msg:
        patch += 1
    elif "#minor" in latest_commit_msg:
        patch = 0
        minor += 1
    elif "#major" in latest_commit_msg:
        patch, minor = 0, 0
        major += 1

    NEW_VER = ".".join([str(i) for i in (major, minor, patch)])

    if NEW_VER == STUDENTFASTREG_VERSION:
        print("No new version marker, skipping")
    else:
        open(os.path.join("studentfastreg", "VERSION.txt"), "w", encoding="utf8").write(
            NEW_VER
        )
        print(f"New version is {NEW_VER}")
        run(f'git add -A . && git commit -m "#bump to {NEW_VER}"')


@task(pre=(update_version_txt,))
def tag(context):
    """Auto add tag to git commit depending on studentfastreg version"""

    STUDENTFASTREG_VERSION = (
        open(os.path.join("studentfastreg", "VERSION.txt"), "r", encoding="utf8")
        .read()
        .strip()
    )

    latest_tag = StringIO()

    run("git describe --abbrev=0 --tags", out_stream=latest_tag, warn=True)
    latest_tag = latest_tag.getvalue().strip()

    if f"v{STUDENTFASTREG_VERSION}" != latest_tag:
        run(f"git tag v{STUDENTFASTREG_VERSION}")
        run("git push --tags")
    else:
        print("No new version, skipping")
