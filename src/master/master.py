import logging
import os
from asyncio import Lock, Queue
from pathlib import Path
from typing import List, Tuple

import grpc
from google.protobuf.empty_pb2 import Empty

from src.generated_files.worker_pb2 import MapTask, MapResponse, ReduceTask
from src.generated_files.worker_pb2_grpc import WorkerStub
from src.generated_files.master_pb2 import (
    RegisterServiceMes,
    MapReduceRequest,
    MapReduceResponse,
)
from src.generated_files.master_pb2_grpc import MasterServicer


class MasterState:
    def __init__(self, shared_dir: Path):
        self.shared_dir = shared_dir
        self.reduce_out_dir = shared_dir / "reduce_output"
        self.map_out_dir = shared_dir / "map_task"

        self.map_tasks_num: int | None = None
        self.reduce_tasks_num: int | None = None

        self.worker_addresses: Tuple[set[str], Lock] = set(), Lock()

        self.completed_map_tasks: Tuple[List[Tuple[MapTask, MapResponse]], Lock] = (
            [],
            Lock(),
        )
        self.completed_reduce_tasks: Tuple[List[ReduceTask], Lock] = [], Lock()

        self.idle_workers: Queue[str] = Queue(32)
        self.idle_map_tasks: Queue[MapTask] = Queue()  # output path and idx
        self.idle_reduce_tasks: Queue[ReduceTask] = Queue()  # output path and idx

    async def initialize_computation(self, input_dir: Path, num_partitions: int):
        logging.info(
            "Master initializing computation for input dir: %s, num partitions: %d",
            input_dir,
            num_partitions,
        )
        self.reduce_tasks_num = num_partitions

        input_files = [
            input_dir / file
            for file in os.listdir(input_dir)
            if not file.startswith(".")
        ]
        self.map_tasks_num = len(input_files)

        # prepares output dirs for map tasks
        self.map_out_dir.mkdir(exist_ok=True)

        for idx, input_file in enumerate(input_files):
            out_dir = self.map_out_dir / f"{str(idx)}"
            out_dir.mkdir(exist_ok=True)

            await self.idle_map_tasks.put(
                MapTask(
                    file_path=input_files[idx].absolute().as_posix(),
                    num_partitions=self.reduce_tasks_num,
                    output_dir=out_dir.absolute().as_posix(),
                )
            )
        logging.info(
            "Master finished initialization for input dir: %s, num partitions: %d",
            input_dir,
            num_partitions,
        )

    async def _add_completed_map_task(
        self, task: MapTask, response: MapResponse
    ) -> bool:
        ret = False

        compl_list, lock = self.completed_map_tasks
        await lock.acquire()
        compl_list.append((task, response))
        if len(compl_list) == self.map_tasks_num:
            ret = True
        lock.release()

        logging.info("Map task %s completed", task.output_dir)
        return ret

    async def _add_completed_reduce_task(self, task: ReduceTask) -> bool:
        ret = False
        compl_list, lock = self.completed_reduce_tasks
        await lock.acquire()
        compl_list.append(task)
        if len(compl_list) == self.reduce_tasks_num:
            ret = True
        lock.release()

        logging.info("Reduce task %s completed", task.output_path)
        return ret

    async def _remove_worker(self, worker: str):
        workers, lock = self.worker_addresses
        await lock.acquire()
        workers.remove(worker)
        lock.release()

    async def add_worker(self, worker: str):
        workers, lock = self.worker_addresses
        await lock.acquire()
        workers.add(worker)
        lock.release()

    async def _consume_map_tasks(self):
        while True:
            idle_task = await self.idle_map_tasks.get()
            next_idle_worker = await self.idle_workers.get()

            logging.info(
                "Sending map task %s to %s", idle_task.file_path, next_idle_worker
            )

            try:
                async with grpc.aio.insecure_channel(next_idle_worker) as channel:
                    map_response = await WorkerStub(channel).Map(idle_task)
            except grpc.RpcError as e:
                logging.warning(
                    "Error when sending map task %s to %s.\nError:%s",
                    idle_task.output_dir,
                    next_idle_worker,
                    e,
                )

                await self._remove_worker(next_idle_worker)
                await self.idle_map_tasks.put(idle_task)
            else:
                await self.idle_workers.put(next_idle_worker)
                if await self._add_completed_map_task(idle_task, map_response):
                    break

    async def _consume_reduce_tasks(self):
        while True:
            idle_task = await self.idle_reduce_tasks.get()
            next_idle_worker = await self.idle_workers.get()

            logging.info(
                "Sending reduce task %s to %s", idle_task.output_path, next_idle_worker
            )

            try:
                async with grpc.aio.insecure_channel(next_idle_worker) as channel:
                    await WorkerStub(channel).Reduce(idle_task)
            except grpc.RpcError as e:
                logging.warning(
                    "Error when sending reduce task %s to %s.\nError:%s",
                    idle_task.output_path,
                    next_idle_worker,
                    e,
                )

                await self._remove_worker(next_idle_worker)
                await self.idle_reduce_tasks.put(idle_task)
            else:
                await self.idle_workers.put(next_idle_worker)
                if await self._add_completed_reduce_task(idle_task):
                    break

    async def _create_reduce_tasks(self):
        # prepares output dir for reduce tasks
        self.reduce_out_dir.mkdir(exist_ok=True)

        reduce_tasks = [
            ReduceTask(
                partition_paths=[],
                output_path=(self.reduce_out_dir / f"reduce_task_{idx}")
                .absolute()
                .as_posix(),
            )
            for idx in range(self.reduce_tasks_num)
        ]

        compl_map_tasks, lock = self.completed_map_tasks
        await lock.acquire()

        for map_req, map_resp in compl_map_tasks:
            for reduce_idx, partition_path in enumerate(map_resp.partition_paths):
                reduce_tasks[reduce_idx].partition_paths.append(partition_path)

        lock.release()

        for reduce_task in reduce_tasks:
            await self.idle_reduce_tasks.put(reduce_task)

    async def mapreduce(self):
        logging.info("Master starting map phase")
        await self._consume_map_tasks()
        logging.info("Master creating reduce tasks")
        await self._create_reduce_tasks()
        logging.info("Master starting reduce phase")
        await self._consume_reduce_tasks()


class Master(MasterServicer):
    def __init__(self, shared_dir: Path):
        self.state = MasterState(shared_dir)

    async def RegisterService(
        self, request: RegisterServiceMes, context: grpc.aio.ServicerContext
    ):
        logging.info(
            "Worker %s : %d registering with master",
            request.service_address,
            request.service_port,
        )
        full_worker_address = f"{request.service_address}:{request.service_port}"
        print(f"Registering worker: {full_worker_address}")
        await self.state.add_worker(full_worker_address)
        await self.state.idle_workers.put(full_worker_address)
        return Empty()

    async def MapReduce(
        self, request: MapReduceRequest, context: grpc.aio.ServicerContext
    ):
        logging.info(
            "Master received MapReduce request.\nInput dir: %s, num_partitions: %d, work_dir: %s",
            request.input_dir,
            request.num_partitions,
            request.work_dir,
        )

        if request.work_dir is not None and request.work_dir != "":
            self.state.map_out_dir = Path(request.work_dir) / "map_task"
            self.state.reduce_out_dir = Path(request.work_dir) / "reduce_output"
        else:
            self.state.map_out_dir = self.state.shared_dir / "map_task"
            self.state.reduce_out_dir = self.state.shared_dir / "reduce_output"

        await self.state.initialize_computation(
            Path(request.input_dir), request.num_partitions
        )
        await self.state.mapreduce()

        logging.info(
            "Master completed MapReduce request.\nInput dir: %s, num_partitions: %d\nResults are in %s. Sending response",
            request.input_dir,
            request.num_partitions,
            self.state.reduce_out_dir,
        )

        return MapReduceResponse(
            output_dir=self.state.reduce_out_dir.absolute().as_posix()
        )
