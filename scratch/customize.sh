SKIPUNZIP=0

ui_print() {
  echo "$1"
}

FRAMEWORK_JAR="$MODPATH/system/framework/framework.jar"

ui_print " "
ui_print "KaoriosToolbox Module"
ui_print "────────────────────────────"

if [ ! -f "$FRAMEWORK_JAR" ]; then
  ui_print "❌ ERROR: framework.jar not found in the module!"
  ui_print "➡️  Please verify the module structure."
  abort
fi

FILE_SIZE=$(stat -c %s "$FRAMEWORK_JAR" 2>/dev/null)


if [ "$FILE_SIZE" -eq 0 ]; then
  ui_print "❌ ERROR: framework.jar is a 0 KB template file"
  ui_print " "
  ui_print "➡️  INSTRUCTIONS:"
  ui_print "   1. Extract the module ZIP"
  ui_print "   2. Replace the file at:"
  ui_print "      system/framework/framework.jar"
  ui_print "   3. Repack the ZIP and flash again"
  ui_print " "
  ui_print "⛔ Installation aborted"
  abort
fi

ui_print "✅ framework.jar is valid."
# Run common tasks for installation and boot-time
if [ -d "$MODPATH/system" ]; then
    . $MODPATH/service.sh
fi

# Clean up any leftover files from previous deprecated methods
rm -f /data/data/com.google.android.gms/cache/pif.prop /data/data/com.google.android.gms/pif.prop \
    /data/data/com.google.android.gms/cache/pif.json /data/data/com.google.android.gms/pif.json
# rm -rf /data/system/dropbox/*
rm -rf /data/system/package_cache/*
