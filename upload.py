import os
import subprocess

#####
# uses https://github.com/prasmussen/gdrive
#####


def getOldFileId(folderId):
    # get the file id
    fileId = subprocess.check_output([
        f"gdrive list --query \"'{folderId}' in parents\" --no-header --name-width 0"], shell=True)
    fileId = fileId.decode("utf-8").split(" ")[0]

    # return the file id
    return fileId


# gdrive: get parentFolderId with parentFolderName
def getParentFolderId(parentFolderName):
    # get the parent folder id
    parentFolderId = subprocess.check_output([
        f"gdrive list --query \"name = '{parentFolderName}'\" --no-header --name-width 0"], shell=True)
    parentFolderId = parentFolderId.decode("utf-8").split(" ")[0]

    # check if the parent folder id is valid
    if parentFolderId == None:
        print("The parent folder wasn't found!")
        exit(1)

    # return the parent folder id
    return parentFolderId


# upload a file to gdrvie as a new revision of the existing file
# tools to be used: gdrive command line tool
def uploadBackup(absFilePath):
    # check if the file exists
    if not os.path.exists(absFilePath):
        print("The file to upload doesn't exist!")
        exit(1)

    # get the file name
    fileName = os.path.basename(absFilePath)

    PARENT_FOLDER_NAME = "kanzlei-backups"
    PARENT_FOLDER_ID = getParentFolderId(PARENT_FOLDER_NAME)

    # get the file id
    fileId = getOldFileId(PARENT_FOLDER_ID)

    # check if the file id is valid
    if fileId.strip() == "":
        print("No file with the given name found!\nUploading as new file...")
        if os.system(
                f"gdrive upload -p {PARENT_FOLDER_ID} --name {fileName} {absFilePath}") != 0:
            print("Upload failed! But idk why...")
    else:
        # upload the file
        if os.system(
                f"gdrive update --name {fileName} {fileId} {absFilePath}") != 0:
            print("Update failed! But idk why...")
