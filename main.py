import asyncio
import json
import os
import random
import signal
from datetime import datetime, timezone

from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient, IoTHubModuleClient

interval = int(os.getenv("INTERVAL_SECONDS", "5"))


async def main():
    global interval

    # Inside IoT Edge the module client is built from the injected environment.
    # For local debugging fall back to the connection string from .env.
    conn_str = os.getenv("EdgeHubConnectionString") or os.getenv(
        "IOTHUB_DEVICE_CONNECTION_STRING"
    )
    is_edge = os.getenv("IOTEDGE_WORKLOADURI") is not None
    if is_edge:
        client = IoTHubModuleClient.create_from_edge_environment()
    elif conn_str:
        client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    else:
        raise RuntimeError(
            "No IoT Edge environment and no EdgeHubConnectionString set"
        )
    await client.connect()

    # Pick up the module twin's desired properties on startup and on change
    twin = await client.get_twin()
    interval = int(twin["desired"].get("intervalSeconds", interval))

    async def on_twin_patch(patch):
        global interval
        if "intervalSeconds" in patch:
            interval = int(patch["intervalSeconds"])
            await client.patch_twin_reported_properties({"intervalSeconds": interval})
            print(f"Interval updated to {interval}s", flush=True)

    client.on_twin_desired_properties_patch_received = on_twin_patch

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            # add_signal_handler is unavailable on Windows event loops.
            signal.signal(sig, lambda *_: loop.call_soon_threadsafe(stop.set))

    print("telemetrysim started", flush=True)
    try:
        while not stop.is_set():
            payload = {
                "temperature": round(random.uniform(20.0, 30.0), 2),
                "humidity": round(random.uniform(40.0, 60.0), 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            msg = Message(json.dumps(payload))
            msg.content_type = "application/json"
            msg.content_encoding = "utf-8"
            if is_edge:
                await client.send_message_to_output(msg, "telemetry")
            else:
                await client.send_message(msg)
            print(f"Sent: {payload}", flush=True)

            try:
                await asyncio.wait_for(stop.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass
    finally:
        await client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())