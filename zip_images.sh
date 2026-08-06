#!
#!/usr/bin/env bash
#
# zip_folders.sh
#
# Zips every immediate subfolder of a target directory into <folder>.zip,
# then deletes the original folder — but only after verifying the zip
# was created successfully and is not corrupt.
#
# Usage:
#   ./zip_folders.sh /path/to/directory
#   ./zip_folders.sh            # defaults to current directory
#
# Tested for Raspberry Pi OS Lite (Debian-based, bash + zip).

set -euo pipefail

TARGET_DIR="/home/pi/images/QuadStar"

# --- Sanity checks -----------------------------------------------------

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: '$TARGET_DIR' is not a directory." >&2
    exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
    echo "Error: 'zip' is not installed. Install it with:" >&2
    echo "    sudo apt update && sudo apt install -y zip unzip" >&2
    exit 1
fi

cd "$TARGET_DIR"

shopt -s nullglob

FOLDERS=(*/)

if [[ ${#FOLDERS[@]} -eq 0 ]]; then
    echo "No subfolders found in '$TARGET_DIR'. Nothing to do."
    exit 0
fi

echo "Target directory: $(pwd)"
echo "Found ${#FOLDERS[@]} folder(s) to zip."
echo

# --- Main loop -----------------------------------------------------------

for folder in "${FOLDERS[@]}"; do
    # Strip trailing slash
    name="${folder%/}"
    zipfile="${name}.zip"

    # Skip if it's not actually a directory (safety, in case of symlinks etc.)
    [[ -d "$name" ]] || continue

    echo "Zipping '$name' -> '$zipfile' ..."

    if [[ -e "$zipfile" ]]; then
        echo "  Warning: '$zipfile' already exists, overwriting."
        rm -f "$zipfile"
    fi

    # Create the zip quietly, preserving folder structure
    if zip -r -q -9 "$zipfile" "$name"; then
        # Verify the zip isn't corrupt before deleting the source
        if unzip -tq "$zipfile" >/dev/null 2>&1; then
            rm -rf -- "$name"
            echo "  Done. Removed original folder."
        else
            echo "  Error: zip verification failed for '$zipfile'. Original folder kept." >&2
            rm -f "$zipfile"
        fi
    else
        echo "  Error: failed to zip '$name'. Original folder kept." >&2
    fi

    echo
done

echo "All done."
