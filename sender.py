import asyncio
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived
from aioquic.asyncio.protocol import QuicConnectionProtocol


class EchoServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            print("Handshake completed.")
        elif isinstance(event, StreamDataReceived):
            print(f"Received data: {event.data.decode()}")
            # Respond with the received data prefixed by "Echo: "
            self._quic.send_stream_data(event.stream_id, b"Echo: " + event.data, end_stream=True)
            # Wait a bit before closing the server
            asyncio.create_task(self.shutdown())

    async def shutdown(self):
        # Wait a few seconds to ensure client receives the response before shutting down the server
        await asyncio.sleep(2)
        self._transport.close()  # Close the connection
        asyncio.get_event_loop().stop()  # Stop the event loop


async def main():
    # Create a QUIC configuration for the server
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    # Start the QUIC server
    print("Starting server...")
    await serve(
        host="127.0.0.1",
        port=4433,
        configuration=configuration,
        create_protocol=EchoServerProtocol,
    )
    print("Server started on 127.0.0.1:4433")

    # Keep the server running (it will stop after echoing the message)
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, but it'll stop sooner
    except KeyboardInterrupt:
        print("Server shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
