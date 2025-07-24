#!/bin/bash
# Runner control script

RUNNER_DIR="/Users/weg/actions-runner"

case "$1" in
    install)
        echo "Installing GitHub Actions runner as service..."
        cd "$RUNNER_DIR" && ./svc.sh install
        ;;
    start)
        echo "Starting GitHub Actions runner service..."
        cd "$RUNNER_DIR" && ./svc.sh start
        ;;
    stop)
        echo "Stopping GitHub Actions runner service..."
        cd "$RUNNER_DIR" && ./svc.sh stop
        ;;
    status)
        echo "Checking GitHub Actions runner service status..."
        cd "$RUNNER_DIR" && ./svc.sh status
        ;;
    uninstall)
        echo "Uninstalling GitHub Actions runner service..."
        cd "$RUNNER_DIR" && ./svc.sh uninstall
        ;;
    run)
        echo "Running GitHub Actions runner in background..."
        cd "$RUNNER_DIR" && nohup ./run.sh > runner.log 2>&1 &
        echo "Runner started with PID: $!"
        echo "Logs: $RUNNER_DIR/runner.log"
        ;;
    logs)
        echo "Showing runner logs..."
        tail -f "$RUNNER_DIR/runner.log"
        ;;
    *)
        echo "Usage: $0 {install|start|stop|status|uninstall|run|logs}"
        echo ""
        echo "Service commands (requires sudo):"
        echo "  install   - Install as macOS service"
        echo "  start     - Start the service"
        echo "  stop      - Stop the service"
        echo "  status    - Check service status"
        echo "  uninstall - Remove the service"
        echo ""
        echo "Background commands:"
        echo "  run       - Run in background with nohup"
        echo "  logs      - View runner logs"
        exit 1
        ;;
esac
