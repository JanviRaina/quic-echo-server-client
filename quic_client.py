import asyncio
import platform
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived
import time

# Workaround for Windows: Using the selector event loop instead of the Proactor event loop
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class EchoClientProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            print("Handshake completed.")
        elif isinstance(event, StreamDataReceived):
            print(f"Received response: {event.data.decode()}")

            # Calculate round-trip time after receiving the response
            end_time = time.time()
            print(f"Total round-trip time: {end_time - self.start_time} seconds")


async def main():
    # Create QUIC configuration
    configuration = QuicConfiguration(is_client=True)
    configuration.load_verify_locations("cert.pem")

    # Connect to the server
    print("Connecting to server...")
    async with connect(
        "127.0.0.1", 4433, configuration=configuration, create_protocol=EchoClientProtocol
    ) as protocol:
        print("Handshake completed. Sending data to server...")

        protocol.start_time = time.time()  # Record the start time before sending the message

        message = f"Hello QUIC Server:{protocol.start_time}"  # Append start time to the message
        protocol._quic.send_stream_data(0, message.encode(), end_stream=True)
        
        await asyncio.sleep(2)  # Wait to receive the response

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            pass  # Ignore the error and continue
