#!/bin/bash
set -e

UDID="${1:-00008120-00064DE22ED1A01E}"
PMD3=$(which pymobiledevice3 2>/dev/null || echo "$HOME/.local/bin/pymobiledevice3")

if [ ! -f "$PMD3" ]; then
    echo "pymobiledevice3 not found. Install: pipx install pymobiledevice3"
    exit 1
fi

echo "Starting RemoteXPC tunnel for device $UDID..."
echo "This requires sudo (iOS 17+ physical device requirement)"
echo ""
sudo "$PMD3" remote start-tunnel --udid "$UDID"
