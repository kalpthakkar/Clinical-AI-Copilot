from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def log_asr_event(event):

    table = Table(title=f"ASR Event ({event.speaker})")

    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Transcript", event.transcript)
    table.add_row("Start", str(event.timestamp_start))
    table.add_row("End", str(event.timestamp_end))

    table.add_row("Latency", f"{event.latency:.2f}")
    table.add_row("Duration", f"{event.audio_duration:.2f}")
    table.add_row("RTFx", f"{event.rtf:.2f}")

    table.add_row("Language", event.language)
    table.add_row("Confidence", f"{event.language_confidence:.2f}")

    console.print(table)


def log_structured_output(bundle):

    console.print(
        Panel.fit(
            str(bundle),
            title="🧠 Structured Clinical Output",
            border_style="green"
        )
    )