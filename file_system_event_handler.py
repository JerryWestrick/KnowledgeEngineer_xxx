from textual.app import App
from textual.worker import Worker
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from messages import FileSystemChangeMessage, Info


class FSEHandler(FileSystemEventHandler):

    def __init__(self, app: App) -> None:
        super().__init__()
        self.app = app
        self.observer = Observer()

        self.observer.schedule(self, 'Memory/', recursive=True)
        t = Worker(self.app, self.observer.start(), name="WatchDog", description="Separate Thread running WatchDog",
                   thread=True)
        self.app.workers.add_worker(t, start=False, exclusive=True)

    def on_any_event(self, event):
        match event.event_type:
            case 'opened' | 'closed':
                pass

            case 'moved' | 'created' | 'modified' | 'deleted':
                self.app.post_message(
                    FileSystemChangeMessage(
                        event.event_type,
                        event.is_directory,
                        event.src_path,
                        getattr(event, "dest_path", "")
                    )
                )

            case _:
                self.app.post_message(
                    Info("on_any_event",
                         f"[cyan]event_Type={event.event_type}, "
                         f"is_dir={event.is_directory}, "
                         f"src_path={event.src_path}, "
                         f"dst_path={getattr(event, 'dest_path', '')}[/]"
                         )
                )
