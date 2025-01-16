import asyncio
import time
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived
from aioquic.asyncio.protocol import QuicConnectionProtocol


class EchoServerProtocol(QuicConnectionProtocol):
    shutdown_event = None  # To be set by the main function

    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            print("Handshake completed.")
        elif isinstance(event, StreamDataReceived):
            message = event.data.decode()
            print(f"Received data: {message}")
            
            # Extract the start_time sent by the client (assuming it's sent as part of the message)
            try:
                start_time = float(message.split(':')[1])  # For example: "Hello QUIC Server:1632342345.2345"
            except IndexError:
                start_time = time.time()  # Default to current time if not available
            
            # Calculate round trip time and print it
            end_time = time.time()
            round_trip_time = end_time - start_time
            print(f"Request-response round trip time: {round_trip_time} seconds")
            
            # Respond with the received data prefixed by "Echo: "
            self._quic.send_stream_data(event.stream_id, f"Echo: {message}".encode(), end_stream=True)

            # Set the shutdown event after responding to the client
            asyncio.create_task(self.shutdown())  # Initiate shutdown

    async def shutdown(self):
        # Wait for the shutdown signal
        await asyncio.sleep(1)
        self._transport.close()  # Close the connection
        if self.shutdown_event:  # Check if shutdown_event is set
            self.shutdown_event.set()  # Signal that the server can shut down


async def main():
    # Create a QUIC configuration for the server
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    # Create a shutdown event and assign it to the protocol
    shutdown_event = asyncio.Event()
    EchoServerProtocol.shutdown_event = shutdown_event

    # Start the QUIC server
    print("Starting server...")
    server = await serve(
        host="127.0.0.1",
        port=4433,
        configuration=configuration,
        create_protocol=EchoServerProtocol,
    )
    print("Server started on 127.0.0.1:4433")

    # Wait for the shutdown signal from the server protocol
    await shutdown_event.wait()  # Wait for shutdown to be signaled

    # Shutdown the server after the event is set
    print("Shutting down the server.")


if __name__ == "__main__":
    asyncio.run(main())
