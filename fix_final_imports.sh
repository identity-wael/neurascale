#!/bin/bash
# Fix final unused import issues

cd /Users/weg/NeuraScale/neurascale

echo "Fixing unused imports in base.py..."
sed -i '' 's/from typing import Dict, List, Optional, Any, Callable, AsyncIterator/from typing import Dict, List, Optional, Any, Callable/' neural-engine/devices/base.py

echo "Fixing unused imports in device_manager.py..."
sed -i '' 's/from datetime import datetime, timedelta/from datetime import datetime/' neural-engine/devices/device_manager.py

echo "Fixing unused imports in device_registry.py..."
sed -i '' 's/from typing import Dict, List, Optional, Any, Callable, Set/from typing import Dict, List, Optional, Any, Callable/' neural-engine/devices/device_registry.py

echo "Fixing unused imports in health_monitor.py..."
# Use more specific sed to only remove the DeviceInfo import
sed -i '' '/from \.base import DeviceInfo/d' neural-engine/devices/health_monitor.py

echo "Done fixing final imports!"
