import rticonnextdds_connector as rti
import time

with rti.open_connector(
        config_name="MyParticipantLibrary::MyPubParticipant",
        url="./config/ShapeExample.xml") as connector:

    output = connector.get_output("MyPublisher::MySquareWriter")

    print("Waiting for subscriptions...")
    output.wait_for_subscriptions()

    print("Writing...")
    for i in range(1, 10000):
        output.instance.set_number("x", i)
        output.instance.set_number("y", i*2)
        output.instance.set_number("shapesize", 30)
        output.instance.set_string("color", "BLUE")
        output.write()

    output.instance.set_string("color", "RED")
    output.write()

    print("Exiting...")
    output.wait() # Wait for all subscriptions to receive the data before exiting