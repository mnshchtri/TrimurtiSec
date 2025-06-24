import time
import asyncio
from typing import Optional, List, Callable, Any
from rich.console import Console
from rich.progress import (
    Progress, ProgressColumn, BarColumn, TextColumn, TimeElapsedColumn, 
    TimeRemainingColumn, SpinnerColumn, MofNCompleteColumn, DownloadColumn,
    TransferSpeedColumn, TaskProgressColumn
)
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from rich.table import Table
from rich.layout import Layout
from contextlib import contextmanager
import threading
import random
from datetime import datetime
from fpdf import FPDF

console = Console()

class CustomSpinnerColumn(ProgressColumn):
    """Custom spinner with enhanced animations"""
    
    def __init__(self, spinner_style="dots12", speed=1.0):
        super().__init__()
        self.spinner_style = spinner_style
        self.speed = speed
        
    def render(self, task):
        if task.finished:
            return Text("✅", style="green")
        elif task.total is None:
            spinner = Spinner(self.spinner_style, style="cyan", speed=self.speed)
            return spinner
        else:
            return Text("🔄", style="blue")

class CustomBarColumn(BarColumn):
    """Enhanced progress bar with gradient colors"""
    
    def __init__(self, bar_width=None, style="bar.back", complete_style="bar.complete", 
                 finished_style="bar.finished", pulse_style="bar.pulse"):
        super().__init__(bar_width, style, complete_style, finished_style, pulse_style)
        
    def render(self, task):
        if task.completed == 0:
            style = "red"
        elif task.completed < task.total * 0.3:
            style = "red"
        elif task.completed < task.total * 0.6:
            style = "yellow"
        elif task.completed < task.total * 0.9:
            style = "green"
        else:
            style = "bright_green"
            
        # Create gradient effect
        bar = super().render(task)
        return Text.from_markup(f"[{style}]{bar}[/{style}]")

class EnhancedProgress:
    """Enhanced progress tracking with eye-catching animations"""
    
    def __init__(self, title: str = "Processing", show_speed: bool = False):
        self.title = title
        self.show_speed = show_speed
        self.console = Console()
        self._setup_progress()
        
    def _setup_progress(self):
        """Setup progress bar with custom columns"""
        columns = [
            CustomSpinnerColumn("dots12", speed=1.5),
            TextColumn("[bold blue]{task.description}", justify="left"),
            CustomBarColumn(bar_width=40),
            MofNCompleteColumn(),
            "•",
            TimeElapsedColumn(),
            "•",
            TimeRemainingColumn(),
        ]
        
        if self.show_speed:
            columns.extend([
                "•",
                TransferSpeedColumn(),
            ])
            
        self.progress = Progress(
            *columns,
            console=self.console,
            refresh_per_second=10,
            speed_estimate_period=30,
        )
        
    @contextmanager
    def track(self, sequence, description: str = "Working...", total: Optional[int] = None):
        """Context manager for tracking progress with enhanced animations"""
        if total is None:
            total = len(sequence) if hasattr(sequence, '__len__') else None
            
        with self.progress:
            task_id = self.progress.add_task(description, total=total)
            
            def update_progress(item):
                self.progress.advance(task_id)
                return item
                
            yield (update_progress(item) for item in sequence)
            
    def create_multi_progress(self, tasks: List[dict]):
        """Create multiple progress bars for concurrent operations"""
        with self.progress:
            task_ids = []
            for task_info in tasks:
                task_id = self.progress.add_task(
                    task_info.get('description', 'Working...'),
                    total=task_info.get('total', 100)
                )
                task_ids.append(task_id)
            return task_ids
            
    def update_task(self, task_id, advance: int = 1, description: Optional[str] = None):
        """Update a specific task"""
        if description:
            self.progress.update(task_id, description=description)
        self.progress.advance(task_id, advance)
        
    def complete_task(self, task_id, description: Optional[str] = None):
        """Mark a task as complete"""
        if description:
            self.progress.update(task_id, description=f"✅ {description}")
        self.progress.update(task_id, completed=self.progress.tasks[task_id].total)

class AnimatedSpinner:
    """Standalone animated spinner for simple operations"""
    
    def __init__(self, message: str = "Processing...", style: str = "dots12"):
        self.message = message
        self.style = style
        self.console = Console()
        self._stop_event = threading.Event()
        self._thread = None
        
    def start(self):
        """Start the animated spinner"""
        def _spin():
            with self.console.status(f"[bold cyan]{self.message}[/bold cyan]", spinner=self.style):
                while not self._stop_event.wait(0.1):
                    pass
                    
        self._thread = threading.Thread(target=_spin)
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self, success_message: Optional[str] = None):
        """Stop the spinner and optionally show success message"""
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            
        if success_message:
            self.console.print(f"✅ [bold green]{success_message}[/bold green]")
            
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.stop("Completed successfully!")
        else:
            self.stop("Operation failed!")

class TrimurtiProgressTracker:
    """Specialized progress tracker for TrimurtiSec operations"""
    
    MODES = {
        'brahma': {'emoji': '🔍', 'color': 'blue', 'name': 'Reconnaissance'},
        'vishnu': {'emoji': '🔐', 'color': 'green', 'name': 'Persistence'},
        'shiva': {'emoji': '💥', 'color': 'red', 'name': 'Exploitation'},
        'god': {'emoji': '👑', 'color': 'gold', 'name': 'Full Control'}
    }
    
    def __init__(self, mode: str, target: str):
        self.mode = mode
        self.target = target
        self.console = Console()
        self.mode_info = self.MODES.get(mode, {'emoji': '⚡', 'color': 'white', 'name': 'Unknown'})
        
    def create_mode_header(self):
        """Create an attractive header for the current mode"""
        emoji = self.mode_info['emoji']
        color = self.mode_info['color']
        name = self.mode_info['name']
        
        header_text = f"{emoji} {name} Mode - Target: {self.target} {emoji}"
        
        panel = Panel(
            Align.center(Text(header_text, style=f"bold {color}")),
            border_style=color,
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
    def create_scan_progress(self, total_steps: int):
        """Create progress tracker for scanning operations"""
        columns = [
            CustomSpinnerColumn("earth", speed=2.0),
            TextColumn(f"[bold {self.mode_info['color']}]{{task.description}}[/bold {self.mode_info['color']}]"),
            CustomBarColumn(bar_width=50),
            TextColumn("[bold blue]{task.completed}[/bold blue]/[bold cyan]{task.total}[/bold cyan]"),
            "•",
            TimeElapsedColumn(),
            "•",
            TextColumn("[bold green]{task.percentage:>3.0f}%[/bold green]")
        ]
        
        return Progress(
            *columns,
            console=self.console,
            refresh_per_second=15,
        )
        
    def show_completion_stats(self, stats: dict):
        """Show completion statistics in a nice table"""
        table = Table(title=f"{self.mode_info['emoji']} Operation Complete", 
                     show_header=True, header_style="bold magenta")
        
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
            
        self.console.print(table)

    def generate_pdf_report(self, stats: dict, output_path: str):
        """Generate a PDF report with a professional design."""
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set fonts
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
        
        # Header
        pdf.set_font('DejaVu', 'B', 24)
        pdf.set_text_color(220, 50, 50)
        pdf.cell(0, 15, 'TrimurtiSec Cyber Operation Report', 0, 1, 'C')
        
        # Sub-header
        pdf.set_font('DejaVu', '', 12)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Operation Details
        pdf.set_font('DejaVu', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'Operation Details', 0, 1, 'L')
        
        pdf.set_font('DejaVu', '', 12)
        pdf.set_fill_color(240, 240, 240)
        
        details = [
            ("Target:", self.target),
            ("Mode:", f"{self.mode_info['emoji']} {self.mode_info['name']}"),
        ]
        
        for title, value in details:
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(40, 10, title, 0, 0, 'L')
            pdf.set_font('DejaVu', '', 12)
            pdf.cell(0, 10, value, 0, 1, 'L')
        pdf.ln(10)

        # Scan Statistics
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Scan Statistics', 0, 1, 'L')
        
        pdf.set_font('DejaVu', 'B', 12)
        pdf.set_fill_color(220, 50, 50)
        pdf.set_text_color(255, 255, 255)
        
        pdf.cell(95, 10, 'Metric', 1, 0, 'C', 1)
        pdf.cell(95, 10, 'Value', 1, 1, 'C', 1)

        pdf.set_font('DejaVu', '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(245, 245, 245)
        
        fill = False
        for key, value in stats.items():
            pdf.cell(95, 10, key, 1, 0, 'L', fill)
            pdf.cell(95, 10, str(value), 1, 1, 'L', fill)
            fill = not fill
        pdf.ln(15)

        # Footer
        pdf.set_y(-30)
        pdf.set_font('DejaVu', '', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, 'CONFIDENTIAL: This report is for authorized personnel only.', 0, 1, 'C')
        pdf.cell(0, 10, 'TrimurtiSec © 2024', 0, 1, 'C')

        try:
            pdf.output(output_path)
            self.console.print(f"✅ [bold green]PDF report generated at: {output_path}[/bold green]")
        except Exception as e:
            if "DejaVuSans.ttf" in str(e):
                self.console.print("[bold red]Error: DejaVu font not found.[/bold red]")
                self.console.print("Please download it from: https://www.fontsquirrel.com/fonts/dejavu-sans")
                self.console.print("And place 'DejaVuSans.ttf' and 'DejaVuSans-Bold.ttf' in your project directory.")
            else:
                self.console.print(f"[bold red]Error generating PDF: {e}[/bold red]")

    def show_live_updates(self, updates: List[str], duration: float = 5.0):
        """Show live scrolling updates"""
        def generate_updates():
            for update in updates:
                yield f"[{time.strftime('%H:%M:%S')}] {update}"
                time.sleep(duration / len(updates))
                
        with Live(console=self.console, refresh_per_second=4) as live:
            for update in generate_updates():
                live.update(Panel(update, border_style=self.mode_info['color']))

def create_hacking_simulation_progress(steps: List[str], target: str):
    """Create a Hollywood-style hacking progress simulation"""
    console = Console()
    
    # Create dramatic header
    header = f"""
    ╔══════════════════════════════════════════════════════╗
    ║           🚀 INITIATING CYBER OPERATION 🚀           ║
    ║                 TARGET: {target:<20}                 ║
    ╚══════════════════════════════════════════════════════╝
    """
    
    console.print(Text(header, style="bold red"))
    
    # Simulate hacking steps with dramatic pauses
    with Progress(
        SpinnerColumn("bouncingBall"),
        TextColumn("[bold green]{task.description}"),
        BarColumn(bar_width=40, style="green", complete_style="bright_green"),
        TaskProgressColumn(),
        console=console,
        refresh_per_second=20
    ) as progress:
        
        for i, step in enumerate(steps):
            task = progress.add_task(f"[PHASE {i+1}] {step}", total=100)
            
            # Simulate varying speeds for dramatic effect
            for _ in range(100):
                time.sleep(random.uniform(0.01, 0.05))  # Realistic timing
                progress.advance(task, 1)
                
            # Brief pause between phases
            time.sleep(0.3)
            progress.update(task, description=f"✅ [PHASE {i+1}] {step} - COMPLETE")
            
    console.print("\n🎯 [bold bright_green]OPERATION SUCCESSFUL![/bold bright_green] 🎯\n")

def demo_enhanced_progress():
    """Demo function to showcase enhanced progress features"""
    console = Console()
    
    # Demo 1: Basic enhanced progress
    console.print("\n[bold blue]Demo 1: Enhanced Progress Bar[/bold blue]")
    ep = EnhancedProgress("TrimurtiSec Demo", show_speed=True)
    
    with ep.track(range(50), "Scanning ports...", 50) as items:
        for item in items:
            time.sleep(0.1)  # Simulate work
            
    # Demo 2: Multi-task progress
    console.print("\n[bold blue]Demo 2: Multi-Task Progress[/bold blue]")
    tracker = TrimurtiProgressTracker("brahma", "example.com")
    tracker.create_mode_header()
    
    with tracker.create_scan_progress(3) as progress:
        tasks = [
            progress.add_task("Port scanning...", total=100),
            progress.add_task("Service detection...", total=80),
            progress.add_task("Vulnerability analysis...", total=60)
        ]
        
        # Simulate concurrent work
        for i in range(100):
            time.sleep(0.02)
            if i < 100: progress.advance(tasks[0])
            if i < 80: progress.advance(tasks[1])
            if i < 60: progress.advance(tasks[2])
            
    # Demo 3: Hacking simulation
    console.print("\n[bold blue]Demo 3: Hacking Simulation[/bold blue]")
    steps = [
        "Establishing connection to target",
        "Bypassing firewall restrictions", 
        "Enumerating active services",
        "Exploiting vulnerabilities",
        "Gaining shell access",
        "Escalating privileges"
    ]
    create_hacking_simulation_progress(steps, "192.168.1.100")

    # Demo 4: PDF Report Generation
    console.print("\n[bold blue]Demo 4: PDF Report Generation[/bold blue]")
    report_tracker = TrimurtiProgressTracker("shiva", "api.example.com")
    report_stats = {
        "Vulnerabilities Found": 5,
        "Critical CVEs": 2,
        "Exploits Attempted": 3,
        "Successful Exploits": 1,
        "Data Exfiltrated": "2.5 GB",
        "Scan Duration": "45.2 minutes"
    }
    report_tracker.show_completion_stats(report_stats)
    report_tracker.generate_pdf_report(report_stats, "trimurti_scan_report.pdf")

if __name__ == "__main__":
    demo_enhanced_progress()

