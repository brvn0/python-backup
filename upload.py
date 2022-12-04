import os
import shutil
import subprocess

#####
# uses https://github.com/prasmussen/gdrive
#####


def delFolder(folderId):
    os.system(f"gdrive delete -r {folderId}")


def mkFolder(name):
    os.system(f"gdrive mkdir {name}")


# gdrive: get parentFolderId with parentFolderName
def getFolderId(name):
    # get the parent folder id
    folderId = subprocess.check_output(
        [f"gdrive list --query \"name = '{name}'\" --no-header --name-width 0"],
        shell=True,
    )
    folderId = folderId.decode("utf-8").split(" ")[0]

    # check if the parent folder id is valid
    if folderId == None:
        print("The parent folder wasn't found!")
        return -1

    # return the parent folder id
    return folderId


def splitFile(absFilePath, tmpDir):
    os.system(
        f"cd {tmpDir} && split -b 3G -d {absFilePath} {os.path.basename(absFilePath)}_split"
    )


def uploadFile(file, parent=-1):
    print(f"gdrive upload {'-p ' + parent if parent != -1 else ''} {file}")
    os.system(f"gdrive upload {'-p ' + parent if parent != -1 else ''} {file}")


# upload a file to gdrvie as a new revision of the existing file
# tools to be used: gdrive command line tool
def uploadBackup(absFilePath, tmpDir="/tmp/.gdriveUpload"):
    # check if the file exists
    if not os.path.exists(absFilePath):
        print("The file to upload doesn't exist!")
        exit(1)

    # get the file name
    fileName = os.path.basename(absFilePath)

    PARENT_FOLDER_NAME = "kanzlei-backups"

    folderId = getFolderId(PARENT_FOLDER_NAME)
    if folderId != -1:
        delFolder(folderId)
    mkFolder(PARENT_FOLDER_NAME)
    folderId = getFolderId(PARENT_FOLDER_NAME)

    print("Done gdrive setup")

    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir)
    os.mkdir(tmpDir)

    print("Created tmp dir")

    print("Splitting file")
    splitFile(absFilePath, tmpDir)
    files = sorted(os.listdir(tmpDir))
    print("Files to be uploaded:", files)
    for file in files:
        uploadFile(tmpDir + "/" + file, folderId)
    print("Upload Done!")
    shutil.rmtree(tmpDir)
    print("Deleted tmpDir")
