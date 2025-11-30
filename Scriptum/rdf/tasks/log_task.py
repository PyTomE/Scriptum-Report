"""Logging helpers for report data file processing."""


class LogTask:
    """Log what is written to check output ordering and contents."""

    def __init__(self, task, comment: bool = False):
        if '=' in task:
            path, value = task.split('=', 1)
            value = value.strip()
            self.fullLine = path.lower().strip() + '=' + value
        else:
            if comment:
                path = '# ' + task  # comment it out
            else:
                # required for new section
                path = task
            #print(comment,path)
            self.fullLine = path.lower().strip()

    def __repr__(self) -> str:
        return self.fullLine
