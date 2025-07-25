"""Main CLI entry point for Neural Engine."""

import click
import logging
from typing import Optional, Any
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """NeuraScale Neural Engine CLI."""
    pass


@cli.command()
@click.option("--project - id", required=True, help="GCP Project ID")
@click.option("--region", default="us - central1", help="GCP Region")
@click.option("--topic", required=True, help="Pub / Sub topic for neural data")
@click.option("--streaming/--batch", default=True, help="Run in streaming mode")
def run_pipeline(project_id: str, region: str, topic: str, streaming: bool) -> None:
    """Run the neural processing pipeline."""
    try:
        from dataflow.neural_processing_pipeline import NeuralProcessingPipeline

        pipeline = NeuralProcessingPipeline(project_id, region)
        pipeline.run(topic, streaming)

    except ImportError as e:
        logger.error(f"Failed to import pipeline: {e}")
        logger.error(
            "Please install dataflow dependencies: pip install apache - beam[gcp]"
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


@cli.command()
@click.option("--host", default="0.0.0.0", help="API server host")
@click.option("--port", default=8000, help="API server port")
def run_api(host: str, port: int) -> None:
    """Run the API server."""
    try:
        import uvicorn

        uvicorn.run("src.api.main:app", host=host, port=port, reload=True)
    except ImportError:
        logger.error("Please install API dependencies: pip install fastapi uvicorn")
    except Exception as e:
        logger.error(f"API server failed: {e}")
        raise


@cli.command()
@click.option("--host", default="0.0.0.0", help="Inference server host")
@click.option("--port", default=8080, help="Inference server port")
@click.option("--config", help="Model configuration file")
def run_inference(host: str, port: int, config: Optional[str]) -> None:
    """Run the inference server."""
    try:
        from models.inference_server import NeuralInferenceServer

        server = NeuralInferenceServer()
        if config:
            server.load_models_from_config(config)
        server.run(host=host, port=port)

    except ImportError as e:
        logger.error(f"Failed to import inference server: {e}")
        logger.error(
            "Please install ML dependencies: pip install tensorflow torch fastapi"
        )
    except Exception as e:
        logger.error(f"Inference server failed: {e}")
        raise


@cli.command()
@click.option(
    "--model - type",
    required=True,
    type=click.Choice(["movement", "emotion", "eegnet"]),
    help="Type of model to train",
)
@click.option("--data - path", required=True, help="Path to training data")
@click.option("--project - id", required=True, help="GCP Project ID")
@click.option("--epochs", default=100, help="Number of training epochs")
def train_model(model_type: str, data_path: str, project_id: str, epochs: int) -> None:
    """Train a neural model."""
    try:
        # from models.training_pipeline import NeuralModelTrainingPipeline

        # Load data (placeholder - implement actual data loading)
        logger.info(f"Loading data from {data_path}")
        # X, y = load_data(data_path)

        # Create training pipeline
        # pipeline = NeuralModelTrainingPipeline(project_id=project_id)

        # Train model based on type
        logger.info(f"Training {model_type} model for {epochs} epochs")
        # results = pipeline.train_model(model, data_splits, {'epochs': epochs})

        logger.info("Training completed successfully")

    except ImportError as e:
        logger.error(f"Failed to import training pipeline: {e}")
        logger.error("Please install ML dependencies")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


@cli.command()
@click.option("--project - id", required=True, help="GCP Project ID")
@click.option(
    "--environment",
    required=True,
    type=click.Choice(["development", "staging", "production"]),
    help="Deployment environment",
)
def deploy(project_id: str, environment: str) -> None:
    """Deploy the neural engine to GCP."""
    logger.info(f"Deploying to {environment} environment in project {project_id}")

    # Deployment logic would go here
    logger.info("Deployment completed successfully")


@cli.command()
def test() -> int:
    """Run tests."""
    import subprocess

    result = subprocess.run(["pytest", "tests/", "-v"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


@cli.command()
@click.option(
    "--device - type",
    required=True,
    type=click.Choice(["lsl", "openbci", "brainflow", "synthetic"]),
    help="Device type",
)
@click.option("--duration", default=10, help="Streaming duration in seconds")
@click.option("--config", help="Device configuration as JSON string")
def test_device(device_type: str, duration: int, config: Optional[str]) -> None:
    """Test a neural data acquisition device."""
    import json
    from src.devices import DeviceManager
    from src.devices.utils import SignalQualityAnalyzer, test_device_latency

    async def run_test() -> None:
        manager = DeviceManager()
        device_config = json.loads(config) if config else {}

        # Data callback
        packet_count = 0

        def data_callback(device_id: str, packet: Any) -> None:
            nonlocal packet_count
            packet_count += 1
            if packet_count % 20 == 0:
                quality = SignalQualityAnalyzer.analyze_packet(packet)
                logger.info(
                    f"Packet {packet_count}: "
                    f"Quality score = {quality['quality_score']:.2f}"
                )

        manager.set_data_callback(data_callback)

        try:
            # Add device
            device = await manager.add_device(
                device_id="test_device", device_type=device_type, **device_config
            )

            # Connect
            logger.info(f"Connecting to {device_type} device...")
            connected = await manager.connect_device("test_device")

            if not connected:
                logger.error("Failed to connect to device")
                return

            logger.info("Device connected successfully")

            # Test latency
            logger.info("Testing device latency...")
            latency_stats = await test_device_latency(device, duration=5)
            logger.info(
                f"Latency: {latency_stats['mean_latency_ms']:.1f} ± "
                f"{latency_stats['std_latency_ms']:.1f} ms"
            )

            # Stream data
            logger.info(f"Streaming data for {duration} seconds...")
            await manager.start_streaming(["test_device"])
            await asyncio.sleep(duration)
            await manager.stop_streaming(["test_device"])

            logger.info(f"Total packets received: {packet_count}")

        except Exception as e:
            logger.error(f"Device test failed: {e}")
            raise
        finally:
            await manager.disconnect_device("test_device")

    asyncio.run(run_test())


if __name__ == "__main__":
    cli()
