def clear_scheduler_state(dask_scheduler):
    dask_scheduler.transition_log.clear()
    dask_scheduler.task_groups.clear()
    dask_scheduler.tasks.clear()
    dask_scheduler.task_prefixes.clear()
    dask_scheduler.task_metadata.clear()
    dask_scheduler.events.clear()
    dask_scheduler.stimulus_log.clear()
    dask_scheduler.unrunnable.clear()
    dask_scheduler.idle.clear()
    dask_scheduler.unknown_tasks.clear()
    dask_scheduler.task_duration.clear()
    dask_scheduler.bandwidth.clear()
    dask_scheduler.task_transfer_inflight.clear()
    dask_scheduler.task_transfer_buffer.clear()

client.run_on_scheduler(clear_scheduler_state)