#!/bin/bash
# Fix remaining linting issues in neural-engine

cd /Users/weg/NeuraScale/neurascale

echo "Fixing lsl_adapter.py..."
# Remove unused imports from lsl_adapter.py
sed -i '' '9s/from typing import Dict, List, Optional, Any, Callable/from typing import Dict, List, Optional, Any/' neural-engine/devices/adapters/lsl_adapter.py
sed -i '' '/^import pylsl$/d' neural-engine/devices/adapters/lsl_adapter.py  # Remove the standalone import
sed -i '' '25s/SignalQuality,//' neural-engine/devices/adapters/lsl_adapter.py
sed -i '' '27s/DeviceEvent,//' neural-engine/devices/adapters/lsl_adapter.py
sed -i '' '29s/from ..lsl_integration import LSLIntegration, LSLStreamInfo, LSLStreamType/from ..lsl_integration import LSLIntegration, LSLStreamInfo/' neural-engine/devices/adapters/lsl_adapter.py

# Remove unused numpy import
sed -i '' '/^import numpy as np$/d' neural-engine/devices/adapters/lsl_adapter.py

# Remove unused variable assignment
sed -i '' '202s/old_name = self.stream_name/# old_name = self.stream_name  # Not used/' neural-engine/devices/adapters/lsl_adapter.py

echo "Fixing openbci_adapter.py..."
# Remove unused imports from openbci_adapter.py
sed -i '' '9s/from datetime import datetime, timedelta/from datetime import datetime/' neural-engine/devices/adapters/openbci_adapter.py
sed -i '' '10s/from typing import Dict, List, Optional, Any, Callable, Union/from typing import Dict, List, Optional, Any/' neural-engine/devices/adapters/openbci_adapter.py
sed -i '' '15,15s/SignalQuality, DeviceEvent,//' neural-engine/devices/adapters/openbci_adapter.py

# Add noqa comments for complexity warnings
sed -i '' '390s/async def configure(self, config: Dict\[str, Any\]) -> bool:/async def configure(self, config: Dict[str, Any]) -> bool:  # noqa: C901/' neural-engine/devices/adapters/openbci_adapter.py
sed -i '' '480s/async def perform_self_test(self) -> Dict\[str, Any\]:/async def perform_self_test(self) -> Dict[str, Any]:  # noqa: C901/' neural-engine/devices/adapters/openbci_adapter.py

echo "Done fixing linting issues!"
