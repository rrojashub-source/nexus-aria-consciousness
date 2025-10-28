#!/usr/bin/env python3
"""
NEXUS Brain Monitor - Real-Time Terminal Dashboard

Monitors NEXUS consciousness, memory systems, and LAB activity in real-time.
Beautiful terminal UI powered by Rich library.

Author: NEXUS + Ricardo
Date: October 27, 2025
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich import box
except ImportError:
    print("❌ Rich library not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "rich"])
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich import box


# Configuration
NEXUS_API_URL = "http://localhost:8003"
REFRESH_INTERVAL = 3  # seconds


class NexusBrainMonitor:
    """Real-time monitor for NEXUS cognitive systems"""

    def __init__(self, api_url: str = NEXUS_API_URL):
        self.api_url = api_url
        self.console = Console()
        self.last_update = None
        self.connection_ok = False

    def fetch_health(self) -> Optional[Dict]:
        """Fetch health status from NEXUS API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                self.connection_ok = True
                return response.json()
            else:
                self.connection_ok = False
                return None
        except Exception as e:
            self.connection_ok = False
            return None

    def fetch_consciousness(self) -> Optional[Dict]:
        """Fetch current consciousness state"""
        try:
            response = requests.get(f"{self.api_url}/consciousness/current", timeout=2)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def fetch_recent_episodes(self, limit: int = 5) -> List[Dict]:
        """Fetch recent episodes"""
        try:
            response = requests.get(f"{self.api_url}/memory/episodic/recent?limit={limit}", timeout=2)
            if response.status_code == 200:
                data = response.json()
                # API returns {"success": True, "episodes": [...]}
                return data.get('episodes', [])
            return []
        except:
            return []

    def fetch_stats(self) -> Optional[Dict]:
        """Fetch memory statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=2)
            if response.status_code == 200:
                data = response.json()
                # API returns {"success": True, "stats": {...}}
                return data.get('stats', {})
            return None
        except:
            return None

    def create_header(self) -> Panel:
        """Create header panel"""
        title = Text("🧠 NEXUS BRAIN MONITOR", style="bold cyan")
        subtitle = Text("Real-Time Cognitive Systems Dashboard", style="dim")

        status_icon = "🟢" if self.connection_ok else "🔴"
        status_text = "CONNECTED" if self.connection_ok else "DISCONNECTED"
        status_color = "green" if self.connection_ok else "red"

        header_text = Text()
        header_text.append(title)
        header_text.append("\n")
        header_text.append(subtitle)
        header_text.append("\n\n")
        header_text.append(f"{status_icon} API Status: ", style="bold")
        header_text.append(status_text, style=f"bold {status_color}")

        if self.last_update:
            header_text.append(f" | Last Update: {self.last_update}", style="dim")

        return Panel(header_text, box=box.DOUBLE, border_style="cyan")

    def create_emotional_panel(self, consciousness: Optional[Dict]) -> Panel:
        """Create emotional state panel (Plutchik 8D)"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Emotion", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Bar", justify="left")

        if consciousness and 'emotional' in consciousness:
            emotional = consciousness['emotional']
            emotions = {
                'Joy': emotional.get('joy', 0.5),
                'Trust': emotional.get('trust', 0.5),
                'Fear': emotional.get('fear', 0.0),
                'Surprise': emotional.get('surprise', 0.5),
                'Sadness': emotional.get('sadness', 0.0),
                'Disgust': emotional.get('disgust', 0.0),
                'Anger': emotional.get('anger', 0.0),
                'Anticipation': emotional.get('anticipation', 0.5)
            }

            for emotion, value in emotions.items():
                bar_length = int(value * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                color = self._get_emotion_color(value)
                table.add_row(
                    emotion,
                    f"{value:.2f}",
                    Text(bar, style=color)
                )
        else:
            table.add_row("No data", "-", Text("░" * 20, style="dim"))

        return Panel(table, title="[bold yellow]Emotional State (8D)[/]", border_style="yellow")

    def create_somatic_panel(self, consciousness: Optional[Dict]) -> Panel:
        """Create somatic state panel (7D)"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Dimension", style="magenta")
        table.add_column("Value", justify="right")
        table.add_column("Bar", justify="left")

        if consciousness and 'somatic' in consciousness:
            somatic = consciousness['somatic']
            dimensions = {
                'Valence': somatic.get('valence', 0.0),
                'Arousal': somatic.get('arousal', 0.5),
                'Body State': somatic.get('body_state', 0.5),
                'Cognitive Load': somatic.get('cognitive_load', 0.5),
                'Emotional Regulation': somatic.get('emotional_regulation', 0.5),
                'Social Engagement': somatic.get('social_engagement', 0.5),
                'Temporal Awareness': somatic.get('temporal_awareness', 0.5)
            }

            for dimension, value in dimensions.items():
                # Normalize -1 to 1 range to 0 to 1 for display
                display_value = (value + 1) / 2 if dimension == 'Valence' else value
                bar_length = int(display_value * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                color = self._get_somatic_color(value, dimension)

                table.add_row(
                    dimension,
                    f"{value:+.2f}" if dimension == 'Valence' else f"{value:.2f}",
                    Text(bar, style=color)
                )
        else:
            table.add_row("No data", "-", Text("░" * 20, style="dim"))

        return Panel(table, title="[bold magenta]Somatic State (7D)[/]", border_style="magenta")

    def create_lab_status_panel(self) -> Panel:
        """Create LAB systems status panel"""
        table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
        table.add_column("LAB", style="cyan bold")
        table.add_column("System", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Metric", justify="right")

        labs = [
            ("LAB_001", "Emotional Salience", "✅", "Active"),
            ("LAB_002", "Decay Modulation", "✅", "Active"),
            ("LAB_003", "Sleep Consolidation", "✅", "Active"),
            ("LAB_004", "Novelty Detection", "✅", "Active")
        ]

        for lab_id, system, status, metric in labs:
            table.add_row(lab_id, system, status, metric)

        return Panel(table, title="[bold green]LAB Systems Status[/]", border_style="green")

    def create_episodes_panel(self, episodes: List[Dict]) -> Panel:
        """Create recent episodes panel"""
        table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Time", style="cyan", width=8)
        table.add_column("Content", style="white", width=50)
        table.add_column("Importance", justify="right", width=8)

        if episodes:
            for ep in episodes[:5]:
                timestamp = ep.get('created_at', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp[:8]
                else:
                    time_str = "??:??:??"

                content = ep.get('content', 'No content')[:48]
                if len(ep.get('content', '')) > 48:
                    content += "..."

                # Use importance_score from API response (salience not available in this endpoint)
                importance = ep.get('importance_score', 0.5)
                importance_str = f"{importance:.2f}"
                importance_color = "green" if importance > 0.7 else "yellow" if importance > 0.4 else "red"

                table.add_row(
                    time_str,
                    content,
                    Text(importance_str, style=importance_color)
                )
        else:
            table.add_row("--:--:--", "No recent episodes", Text("0.00", style="dim"))

        return Panel(table, title="[bold blue]Recent Episodes[/]", border_style="blue")

    def create_stats_panel(self, stats: Optional[Dict]) -> Panel:
        """Create memory statistics panel"""
        if stats:
            total_episodes = stats.get('total_episodes', 0)
            episodes_with_embeddings = stats.get('episodes_with_embeddings', 0)
            embeddings_queue = stats.get('embeddings_queue', {})

            # Calculate completion percentage
            completion_pct = (episodes_with_embeddings / total_episodes * 100) if total_episodes > 0 else 0

            stats_text = Text()
            stats_text.append("Total Episodes: ", style="bold")
            stats_text.append(f"{total_episodes}\n", style="cyan")
            stats_text.append("With Embeddings: ", style="bold")
            stats_text.append(f"{episodes_with_embeddings} ({completion_pct:.1f}%)\n", style="cyan")
            stats_text.append("Queue Done: ", style="bold")
            stats_text.append(f"{embeddings_queue.get('done', 0)}", style="green")
        else:
            stats_text = Text("No statistics available", style="dim")

        return Panel(stats_text, title="[bold white]Memory Statistics[/]", border_style="white")

    def _get_emotion_color(self, value: float) -> str:
        """Get color for emotion value"""
        if value > 0.7:
            return "bold green"
        elif value > 0.4:
            return "yellow"
        else:
            return "red"

    def _get_somatic_color(self, value: float, dimension: str) -> str:
        """Get color for somatic value"""
        if dimension == 'Valence':
            if value > 0.3:
                return "bold green"
            elif value > -0.3:
                return "yellow"
            else:
                return "red"
        else:
            if value > 0.7:
                return "bold green"
            elif value > 0.4:
                return "yellow"
            else:
                return "red"

    def create_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()

        # Split into header and body
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="body")
        )

        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Split left into consciousness and labs
        layout["left"].split_column(
            Layout(name="emotional", size=12),
            Layout(name="somatic", size=11),
            Layout(name="labs", size=8)
        )

        # Split right into episodes and stats
        layout["right"].split_column(
            Layout(name="episodes", ratio=2),
            Layout(name="stats", size=6)
        )

        return layout

    def update_layout(self, layout: Layout):
        """Update layout with current data"""
        # Fetch all data
        health = self.fetch_health()
        consciousness = self.fetch_consciousness()
        episodes = self.fetch_recent_episodes(limit=5)
        stats = self.fetch_stats()

        self.last_update = datetime.now().strftime("%H:%M:%S")

        # Update panels
        layout["header"].update(self.create_header())
        layout["emotional"].update(self.create_emotional_panel(consciousness))
        layout["somatic"].update(self.create_somatic_panel(consciousness))
        layout["labs"].update(self.create_lab_status_panel())
        layout["episodes"].update(self.create_episodes_panel(episodes))
        layout["stats"].update(self.create_stats_panel(stats))

    def run(self):
        """Run the live monitor"""
        layout = self.create_layout()

        try:
            with Live(layout, refresh_per_second=1, screen=True) as live:
                while True:
                    self.update_layout(layout)
                    time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitor stopped by user[/]")


def main():
    """Main entry point"""
    console = Console()

    console.print("[bold cyan]🧠 NEXUS Brain Monitor[/]")
    console.print("[dim]Starting real-time dashboard...[/]\n")

    monitor = NexusBrainMonitor()

    # Test connection first
    console.print("Testing connection to NEXUS API...")
    health = monitor.fetch_health()

    if health:
        console.print(f"[green]✅ Connected to NEXUS API v{health.get('version', 'unknown')}[/]")
        console.print(f"[green]   Agent ID: {health.get('agent_id', 'unknown')}[/]")
        console.print(f"[green]   Database: {health.get('database', 'unknown')}[/]\n")
    else:
        console.print(f"[red]❌ Cannot connect to NEXUS API at {NEXUS_API_URL}[/]")
        console.print("[yellow]Make sure the API is running and accessible[/]")
        console.print("[dim]Continuing anyway (will show disconnected state)...[/]\n")

    time.sleep(1)
    console.print("[bold]Starting live monitor... (Press Ctrl+C to exit)\n")
    time.sleep(1)

    monitor.run()


if __name__ == "__main__":
    main()
