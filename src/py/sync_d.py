import os
import shutil
import datetime
import filecmp
import argparse
import sys

def sync_path(from_path, to_path):
    changes = []

    if os.path.isfile(from_path):
        to_dir = os.path.dirname(to_path)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
            changes.append(f"CREATED DIR: {to_dir}")
        
        if not os.path.exists(to_path) or not filecmp.cmp(from_path, to_path, shallow=True):
            shutil.copy2(from_path, to_path)
            changes.append(f"UPDATED FILE: {to_path}")
        return changes

    if not os.path.isdir(from_path):
        return changes

    if not os.path.exists(to_path):
        os.makedirs(to_path)
        changes.append(f"CREATED DIR: {to_path}")

    for src_dir, _, files in os.walk(from_path):
        dest_dir = src_dir.replace(from_path, to_path, 1)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            changes.append(f"CREATED DIR: {dest_dir}")

        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dest_file = os.path.join(dest_dir, file_)
            if not os.path.exists(dest_file) or not filecmp.cmp(src_file, dest_file, shallow=True):
                shutil.copy2(src_file, dest_file)
                changes.append(f"UPDATED FILE: {dest_file}")

    for dest_dir, dirs, files in os.walk(to_path, topdown=False):
        for file_ in files:
            dest_file = os.path.join(dest_dir, file_)
            src_file = dest_file.replace(to_path, from_path, 1)
            if not os.path.exists(src_file):
                os.remove(dest_file)
                changes.append(f"DELETED FILE: {dest_file}")
        
        for dir_ in dirs:
            dest_subdir = os.path.join(dest_dir, dir_)
            src_subdir = dest_subdir.replace(to_path, from_path, 1)
            if not os.path.exists(src_subdir):
                try:
                    shutil.rmtree(dest_subdir)
                    changes.append(f"DELETED DIR: {dest_subdir}")
                except OSError as e:
                    print(f"INFO: Could not remove {dest_subdir}, it may have been already deleted. Error: {e}")
    return changes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script to synchronize files between source and destination.",
        epilog="Example usage: python your_script_name.py -b"
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "-b", "--backup", 
        action="store_true", 
        help="Run in BACKUP mode: Syncs from original location to backup location."
    )
    mode_group.add_argument(
        "-r", "--restore", 
        action="store_true", 
        help="Run in RESTORE mode: Syncs from backup location to original location. USE WITH CAUTION!"
    )
    args = parser.parse_args()

    path_map = [
        {"original": "/mnt/c/Users/JiaoYuan/Documents/NetSarang Computer", "backup": "/mnt/d/BACKUP/JiaoYuan/Documents/NetSarang Computer"},
        {"original": "/mnt/c/Users/JiaoYuan/Documents/My Games", "backup": "/mnt/d/BACKUP/JiaoYuan/Documents/My Games"},
        {"original": "/mnt/c/Users/JiaoYuan/Pictures", "backup": "/mnt/d/BACKUP/JiaoYuan/Pictures"},
        {"original": "/mnt/c/Users/JiaoYuan/.ssh", "backup": "/mnt/d/BACKUP/JiaoYuan/.ssh"},
        {"original": "/mnt/c/Users/JiaoYuan/.wslconfig", "backup": "/mnt/d/BACKUP/JiaoYuan/.wslconfig"},
        {"original": "/mnt/c/User/JiaoYuan/Desktop/MISC/CV.pdf", "backup": "/mnt/d/BACKUP/JiaoYuan/Desktop/MISC/CV.pdf"},
        {"original": "/mnt/c/Scoop/apps/rclone/current/rclone.conf", "backup": "/mnt/d/BACKUP/Scoop/apps/rclone/rclone.conf"},
        {"original": "/mnt/c/Scoop/apps/vscode/current/data/user-data/User/settings.json", "backup": "/mnt/d/BACKUP/Scoop/apps/vscode/current/data/user-data/User/settings.json"},
        {"original": "/home/jy/.bashrc", "backup": "/mnt/d/BACKUP/jy/.bashrc"},
        {"original": "/home/jy/.gitconfig", "backup": "/mnt/d/BACKUP/jy/.gitconfig"},
        {"original": "/home/jy/.git-credentials", "backup": "/mnt/d/BACKUP/jy/.git-credentials"},
        {"original": "/home/jy/.condarc", "backup": "/mnt/d/BACKUP/jy/.condarc"},
        {"original": "/home/jy/.Rprofile", "backup": "/mnt/d/BACKUP/jy/.Rprofile"},
        {"original": "/home/jy/.npmrc", "backup": "/mnt/d/BACKUP/jy/.npmrc"},
        {"original": "/home/jy/.config/rclone", "backup": "/mnt/d/BACKUP/jy/.config/rclone"},
        {"original": "/home/jy/work/2fa", "backup": "/mnt/d/BACKUP/jy/work/2fa"},
    ]
    
    mode = "BACKUP" if args.backup else "RESTORE"

    print(f"{mode} process started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if mode == "RESTORE":
        print("\n" + "="*60)
        print("!! WARNING: YOU ARE IN RESTORE MODE !!")
        print("This will OVERWRITE files in their original locations using the backup copies.")
        print("Any changes made to original files since the last backup will be LOST.")
        print("="*60 + "\n")
        confirm = input("Are you absolutely sure you want to continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Restore operation cancelled by user.")
            sys.exit(0)

    total_changes = 0
    for paths in path_map:
        if mode == "BACKUP":
            from_path = paths["original"]
            to_path = paths["backup"]
        else:
            from_path = paths["backup"]
            to_path = paths["original"]

        if not os.path.exists(from_path):
            print(f"WARNING: Source path does not exist, skipping: {from_path}")
            continue
        
        try:
            changes_made = sync_path(from_path, to_path)
            if changes_made:
                total_changes += len(changes_made)
                print(f"\n[{mode}] '{from_path}' -> '{to_path}'")
                for change in changes_made:
                    print(f"  - {change}")
        except Exception as e:
            print(f"ERROR: A critical error occurred while syncing '{from_path}': {e}")

    print(f"\n{mode} process finished. Total changes: {total_changes}")