#!/usr/bin/env bash
#
# archive_folders.sh
#
# Archives every immediate subfolder of a target directory into
# <folder>.tar.zst using zstd's --ultra -22 (max compression), then
# deletes the original folder — but only after verifying the archive
# was created successfully and is not corrupt.
#
# Usage:
#   ./archive_folders.sh /path/to/directory
#   ./archive_folders.sh            # defaults to current directory
#
# Tested for Raspberry Pi OS Lite (Debian-based, bash + tar + zstd).

set -euo pipefail

TARGET_DIR="${1:-/home/pi/images/QuadStar}"

# --- Sanity checks -----------------------------------------------------

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: '$TARGET_DIR' is not a directory." >&2
    exit 1
fi

if ! command -v zstd >/dev/null 2>&1; then
    echo "Error: 'zstd' is not installed. Install it with:" >&2
    echo "    sudo apt update && sudo apt install -y zstd" >&2
    exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
    echo "Error: 'tar' is not installed (unusual — should be preinstalled)." >&2
    exit 1
fi

cd "$TARGET_DIR"

shopt -s nullglob

FOLDERS=(*.done/)

if [[ ${#FOLDERS[@]} -eq 0 ]]; then
    echo "No subfolders found in '$TARGET_DIR'. Nothing to do."
    exit 0
fi

echo "Target directory: $(pwd)"
echo "Found ${#FOLDERS[@]} folder(s) to archive."
echo

# --- Main loop -----------------------------------------------------------

for folder in "${FOLDERS[@]}"; do
    # Strip trailing slash
    name="${folder%/}"
    archive="${name}.tar.zst"

    # Skip if it's not actually a directory (safety, in case of symlinks etc.)
    [[ -d "$name" ]] || continue

    echo "Archiving '$name' -> '$archive' ..."

    if [[ -e "$archive" ]]; then
        echo "  Warning: '$archive' already exists, overwriting."
        rm -f "$archive"
    fi

    # Create the archive with zstd -5 (good middle group compression).
    if tar -I 'zstd -5' -cf "$archive" "$name"; then
        # Verify the archive isn't corrupt before deleting the source
        if zstd -t "$archive" >/dev/null 2>&1; then
            rm -rf -- "$name"
            echo "  Done. Removed original folder."
        else
            echo "  Error: archive verification failed for '$archive'. Original folder kept." >&2
            rm -f "$archive"
        fi
    else
        echo "  Error: failed to archive '$name'. Original folder kept." >&2
    fi

    echo
done

echo "All done."
