import rticonnextdds_connector
import rticonnextdds_connector as rti
import asyncio
import datetime

class MyListener:

    def __init__(self):
        self._connector = rti.open_connector(
            config_name="MyParticipantLibrary::MySubParticipant",
            url="./config/ShapeExample.xml")

        self._print_queue = asyncio.Queue()

        self._start_time = None
        self._end_time = 0
        self._rx_msgs = 0
        self._alive = True

    def _get_data(self, loop: asyncio.BaseEventLoop):
        with self._connector as c:

            input = c.get_input("MySubscriber::MySquareReader")
            print("Waiting for publications....")
            input.wait_for_publications()

            print("Waiting for data...")

            while self._alive:
                try:
                    input.wait(timeout=5)
                except rticonnextdds_connector.TimeoutError:
                    break

                input.take()

                for sample in input.samples.valid_data_iter:
                    loop.call_soon_threadsafe(self._print_queue.put_nowait, sample.get_dictionary())

    async def _print_from_queue(self):

        while self._alive:
            data = await self._print_queue.get()
            self._rx_msgs += 1

            if self._start_time is None:
                self._start_time = datetime.datetime.now().timestamp()

            if data['color'] == "RED":
                print("DONE!")
                self._end_time = datetime.datetime.now().timestamp()
                diff = self._end_time - self._start_time
                mps = self._rx_msgs / diff
                print(f"Received {self._rx_msgs} messages in {diff} seconds. {mps=}")
                self._alive = False

            self._print_queue.task_done()

    async def _background_task(self):
        while self._alive:
            await asyncio.sleep(2.0)
            print("Testing ability to run asyncornous tasks!")

    async def start(self):
        loop = asyncio.get_running_loop()

        loop.run_in_executor(None, self._get_data, loop)

        await asyncio.gather(self._background_task(), self._print_from_queue())


a = MyListener()
asyncio.run(a.start())


