import argparse
import time
from pathlib import Path

from db import DB
from logger import Logger
from step import Step
import asyncio
import shutil


log = Logger(namespace="ke", debug=True)
memory = DB()


async def execute_process(process_name: str):
    log.info(f"Begin Execution of Process {process_name}")
    step_no: int = 1
    start_time: float = time.time()
    e_stats = {}
    full_step_names = memory.glob_files(f"{process_name}/Process/*.kestep")
    full_step_names.sort()
    for full_file_names in full_step_names:
        dirs = full_file_names.split('/')
        sname = dirs[-1]
        pname = '/'.join(dirs[:-2])
        step = Step.from_file(pname, sname)
        log.info(f"Execute {process_name}({step_no}): {step.name} ")
        await step.run(process_name)
        for k, v in step.ai.e_stats.items():
            e_stats[k] = e_stats.get(k, 0.0) + v

        step_no += 1
    e_stats['elapsed_time'] = time.time() - start_time
    mins, secs = divmod(e_stats['elapsed_time'], 60)
    head_len = 12
    head = ' ' * head_len

    log.info(f"Elapsed: {int(mins)}m {secs:.2f}s Token Usage: "
                   f"Total: [green]{e_stats['total_tokens']:,}[/] ("
                   f"Prompt: {int(e_stats['prompt_tokens']):,}, "
                   f"Completion: {int(e_stats['completion_tokens']):,})"
                   f"\n{log.ts()}{head}"
                   f"Costs:: Total: [green]${e_stats['s_total']:.2f}[/] "
                   f"(Prompt: ${e_stats['sp_cost']:.4f}, "
                   f"Completion: ${e_stats['sc_cost']:.4f})")


def create_new_proc(proc_name: str) -> None:
    log.info(f"In Create Proc {proc_name}")
    # Copy ExampleProcess directory to Memory/{proc_name}
    shutil.copytree('./ExampleProcess', f'./Memory/{proc_name}')


def list_all_processes():
    proc_list = f"List of all Processes:"
    proc_names = memory.glob_files("*")
    proc_names.sort()
    for proc_name in proc_names:
        proc_list = f"{proc_list}\n{proc_name}"
        step_names = memory.glob_files(f"{proc_name}/Process/*.kestep")
        step_names.sort()
        for step_full_name in step_names:
            step_name = Path(step_full_name).stem
            proc_list = f"{proc_list}\n    {step_name}"

    log.info(proc_list)


async def main(args):

    # Now you can access the arguments as follows
    if not args.proc and not args.create and not args.list:
        log.warn("No Option chosen.")
        parser.print_help()
        exit(1)

    if args.list:
        list_all_processes()
        exit(0)

    log_file = None
    if args.file is not None:
        log.log_file(args.file)
        log.info(f"Logging to: {args.file}")

    if args.create:
        log.info(f"Create new process {args.create}")
        full_proc_names = memory.glob_files(args.create)
        if args.create in full_proc_names:
            log.error(f"Proc {args.create} already exists")
        else:
            create_new_proc(args.create)
        return

    if args.proc:
        if args.step:
            step = Step.from_file(pname=args.proc, sname=args.step)
            await step.run(args.proc)
        else:
            await execute_process(args.proc)

    if log_file is not None:
        # log_file.close()
        log.info(f"Logging to: {log_file.name} complete")


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Knowledge Engineering: AI Prompt Memory Engineering Tool")
    # Add the arguments
    parser.add_argument("-proc", metavar="proc_name", type=str, help="execute the given process name")
    parser.add_argument("-step", metavar="step_name", type=str, help="execute the given step in the proc")
    parser.add_argument("-file", metavar="file_name", type=str, help="Log to the specified file")
    parser.add_argument("-create", metavar="create", type=str, help="Create a process with given name")
    parser.add_argument("-list", action='store_true', help="List all Processes and Steps")

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()

    asyncio.run(main(args))
