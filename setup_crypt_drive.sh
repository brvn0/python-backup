DRIVE='/dev/sdd'
MOUNTPOINT='/backups'
KEYFILE='/raid-crypt.key'
ALIAS='backups'

shred -v -n 1 $DRIVE

# Create a luks partition on the drive
cryptsetup -c aes-cbc-essiv:sha256 -y -s 256 luksFormat $DRIVE --key-file $KEYFILE

# Open the luks partition with alias 'backup-drive'
cryptsetup luksOpen $DRIVE backup-drive --key-file $KEYFILE

# add the alias to /etc/crypttab
UUID=$(blkid -s UUID -o value $DRIVE)
echo "$ALIAS $DRIVE $KEYFILE luks" >> /etc/crypttab

# ext4 filesystem on the luks partition
mkfs.ext4 -m 0 -L $ALIAS /dev/mapper/backup-drive

mkdir $MOUNTPOINT

# Mount the filesystem
mount /dev/mapper/backup-drive $MOUNTPOINT

# Append the mount to /etc/fstab
echo "/dev/mapper/backup-drive $MOUNTPOINT ext4 defaults 0 2" >> /etc/fstab

# Change the owner of the mountpoint
chown -R root:root $MOUNTPOINT

mkdir $MOUNTPOINT/thomas
mkdir $MOUNTPOINT/andi
mkdir $MOUNTPOINT/public

# Change the permissions of the mountpoint
chmod -R 777 $MOUNTPOINT

chown -R thomas:kanzlei $MOUNTPOINT/thomas
chown -R andi:kanzlei $MOUNTPOINT/andi
chown -R thomas:kanzlei $MOUNTPOINT/public
