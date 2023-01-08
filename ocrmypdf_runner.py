import os
import shutil
import subprocess
import sys


def workFile(input, output):
    pass


def getConfig(user):
    config = {
        "in": "/data/smb/thomas-priv/ocrmypdf/in/"
        if user == "thomas"
        else "/data/smb/andi-priv/ocrmypdf/in/",
        "out": "/data/smb/thomas-priv/ocrmypdf/out/"
        if user == "thomas"
        else "/data/smb/thomas-priv/ocrmypdf/out/",
        "extensions": "pdf,jpg,jpeg,tif,tiff,png,gif",
        "binary": "ocrmypdf",  # needs ocrmypdf installed in path!
        "parameters": "-l deu --rotate-pages --output-type pdf --skip-text",
    }

    return config


def touchFile(fileName, times=None):
    if os.path.exists(fileName):
        os.utime(fileName, None)
    else:
        os.mknod(fileName)


def main(config):
    if os.path.exists(config["in"] + ".~ocrLock"):
        print("Lockfile exists! Aborting...")
        return  # in case another instance of this is already running in that input dir
    else:
        touchFile(config["in"] + ".~ocrLock")
    for file in os.listdir(config["in"]):
        if file == ".~ocrLock":
            continue
        if file.split(".")[-1] in config["extensions"]:
            in_file = config["in"] + file
            out_file = config["out"] + "_tmp" + file
            try:
                filePerms = os.stat(in_file)
            except:
                print(f"Can't retrieve file terms for file {file}")
            cmd = f"{config['binary']} {config['parameters']} {in_file} {out_file}"
            print(cmd)
            exception = False
            try:
                process = subprocess.Popen([cmd], shell=True)
                process.wait()
            except:
                print(f"\n\nError!!!!!!! {file}\n\n")
                exception = True
            if process.returncode != 0 or exception:
                print(
                    f"DANGER!!! File {file} just dropped non 0 exit code; still copying it but I told u\nhere's ya error: {process.stdout}\n Exit code: {process.returncode}{' IT DROPPED AN EXECUTION ERROR!!!!' if exception else ''}"
                )
                try:
                    shutil.move(in_file, out_file)
                except:
                    print(
                        f"Error: In consequence of a previous error, moving {file} failed!\nSkipping to the next file!!!"
                    )
                    continue
            else:
                try:
                    os.remove(in_file)
                except:
                    print(f"FileNotFoundException while deleting input file: {file}")
            try:
                os.chown(out_file, filePerms.st_uid, filePerms.st_gid)
                os.chmod(out_file, filePerms.st_mode)
            except:
                print("RAMicro war schneller")
            os.rename(out_file, config["out"] + file)
            print(f"done with file: {file}\n")
        else:
            print(f"skipping {file} bc of wrong extension")
    os.remove(config["in"] + ".~ocrLock")


if __name__ == "__main__":
    if sys.argv[1] is not None:
        main(getConfig(sys.argv[1]))
    else:
        print("No username given!")
        exit(1)
