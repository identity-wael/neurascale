#!/bin/bash
# Fix all remaining monitoring module linting issues

cd /Users/weg/NeuraScale/neurascale

echo "Fixing health_checker.py..."
sed -i '' '/^import aiohttp$/d' neural-engine/monitoring/collectors/health_checker.py
sed -i '' 's/from datetime import datetime, timedelta/from datetime import datetime/' neural-engine/monitoring/collectors/health_checker.py

echo "Fixing opentelemetry_tracer.py..."
sed -i '' 's/from typing import Dict, List, Optional, Any, Union/from typing import Dict, Optional, Any/' neural-engine/monitoring/collectors/opentelemetry_tracer.py

echo "Fixing prometheus_collector.py..."
sed -i '' '/from prometheus_client import CONTENT_TYPE_LATEST/d' neural-engine/monitoring/collectors/prometheus_collector.py
sed -i '' 's/from datetime import datetime/# from datetime import datetime/' neural-engine/monitoring/collectors/prometheus_collector.py
sed -i '' 's/from typing import Dict, List, Optional, Any, Union/from typing import Dict, List, Any/' neural-engine/monitoring/collectors/prometheus_collector.py

echo "Fixing grafana_dashboards.py..."
sed -i '' 's/from datetime import datetime/# from datetime import datetime/' neural-engine/monitoring/dashboards/grafana_dashboards.py
sed -i '' '/^import aiohttp$/d' neural-engine/monitoring/dashboards/grafana_dashboards.py

echo "Fixing prometheus_exporter.py..."
sed -i '' 's/from typing import Dict, List, Optional, Any/from typing import Dict, Optional, Any/' neural-engine/monitoring/exporters/prometheus_exporter.py
sed -i '' '/from prometheus_client import start_http_server/d' neural-engine/monitoring/exporters/prometheus_exporter.py
sed -i '' '/^import aiohttp$/d' neural-engine/monitoring/exporters/prometheus_exporter.py

echo "Fixing device_metrics.py..."
sed -i '' 's/from typing import Dict, List, Optional, Any, Set/from typing import Dict, List, Optional, Any/' neural-engine/monitoring/metrics/device_metrics.py

echo "Done fixing monitoring modules!"
