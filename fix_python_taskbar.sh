#!/bin/bash

echo "This script will modify Python.app's Info.plist to prevent it from appearing in the taskbar."
echo "This affects ALL Python Framework applications on your system."
echo ""

# Backup the original
echo "Creating backup..."
sudo cp /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/Info.plist /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/Info.plist.backup

# Copy the modified version
echo "Installing modified Info.plist..."
sudo cp /Users/03x11/dynamic/Python_Info_modified.plist /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/Info.plist

echo ""
echo "Done! The modified Info.plist has been installed."
echo "Backup saved to: /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/Info.plist.backup"
echo ""
echo "To test, kill all running Python processes and relaunch your Dynamic Island app:"
echo "  pkill -f 'dynamic_island'"
echo "  open '/Users/03x11/dynamic/Dynamic Island.app'"
