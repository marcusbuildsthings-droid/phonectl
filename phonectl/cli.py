"""CLI interface for phonectl."""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .device import Device, DeviceError, NoDeviceError

console = Console()


def get_device(udid: str = None) -> Device:
    """Get a device instance, auto-selecting if no UDID provided."""
    if not udid:
        udid = Device.get_first_device()
        if not udid:
            console.print("[red]No device found.[/red]")
            console.print("Make sure your device is connected via USB and trusted.")
            raise SystemExit(1)
    return Device(udid)


@click.group()
@click.version_option()
def main():
    """phonectl - Simple CLI for iOS device control.
    
    Control your iPhone/iPad from the command line. Take screenshots,
    manage apps, browse files, and more.
    
    Requires pymobiledevice3 and a connected iOS device.
    """
    pass


@main.command()
def list():
    """List connected iOS devices."""
    try:
        devices = Device.list_devices()
        
        if not devices:
            console.print("[yellow]No devices found.[/yellow]")
            console.print("Make sure your device is connected via USB and trusted.")
            return
        
        table = Table(title="Connected Devices")
        table.add_column("UDID", style="cyan")
        table.add_column("Name", style="green")
        
        for device in devices:
            table.add_row(
                device.get("udid", "Unknown"),
                device.get("name", "Unknown")
            )
        
        console.print(table)
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("--udid", "-u", help="Device UDID (auto-selects if not provided)")
@click.option("--output", "-o", default="screenshot.png", help="Output file path")
def screenshot(udid: str, output: str):
    """Take a screenshot of the device screen."""
    try:
        device = get_device(udid)
        path = device.screenshot(output)
        console.print(f"[green]Screenshot saved:[/green] {path}")
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("--udid", "-u", help="Device UDID")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all apps (including system)")
def apps(udid: str, show_all: bool):
    """List installed applications."""
    try:
        device = get_device(udid)
        app_list = device.list_apps(user_only=not show_all)
        
        if not app_list:
            console.print("[yellow]No apps found.[/yellow]")
            return
        
        table = Table(title="Installed Apps")
        table.add_column("Bundle ID", style="cyan")
        table.add_column("Name", style="green")
        
        for app in app_list:
            table.add_row(app["bundle_id"], app.get("name", ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(app_list)} apps[/dim]")
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.argument("bundle_id")
@click.option("--udid", "-u", help="Device UDID")
def launch(bundle_id: str, udid: str):
    """Launch an app by bundle ID."""
    try:
        device = get_device(udid)
        if device.launch_app(bundle_id):
            console.print(f"[green]Launched:[/green] {bundle_id}")
        else:
            console.print(f"[red]Failed to launch:[/red] {bundle_id}")
            raise SystemExit(1)
            
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.argument("bundle_id")
@click.option("--udid", "-u", help="Device UDID")
def kill(bundle_id: str, udid: str):
    """Kill a running app by bundle ID."""
    try:
        device = get_device(udid)
        if device.kill_app(bundle_id):
            console.print(f"[green]Killed:[/green] {bundle_id}")
        else:
            console.print(f"[yellow]App may not be running:[/yellow] {bundle_id}")
            
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("--udid", "-u", help="Device UDID")
def info(udid: str):
    """Show device information."""
    try:
        device = get_device(udid)
        device_info = device.get_device_info()
        
        table = Table(title="Device Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        # Show key properties first
        priority_keys = [
            "DeviceName", "ProductType", "ProductVersion",
            "BuildVersion", "SerialNumber", "UniqueDeviceID"
        ]
        
        for key in priority_keys:
            if key in device_info:
                table.add_row(key, device_info[key])
        
        # Then the rest
        for key, value in device_info.items():
            if key not in priority_keys:
                table.add_row(key, str(value)[:50])
        
        console.print(table)
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.group()
def files():
    """File operations on device."""
    pass


@files.command("ls")
@click.argument("path", default="/")
@click.option("--udid", "-u", help="Device UDID")
def files_ls(path: str, udid: str):
    """List files at path on device."""
    try:
        device = get_device(udid)
        file_list = device.list_files(path)
        
        if not file_list:
            console.print(f"[yellow]No files at:[/yellow] {path}")
            return
        
        for f in file_list:
            console.print(f)
        
        console.print(f"\n[dim]Total: {len(file_list)} items[/dim]")
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@files.command("pull")
@click.argument("remote_path")
@click.argument("local_path")
@click.option("--udid", "-u", help="Device UDID")
def files_pull(remote_path: str, local_path: str, udid: str):
    """Pull a file from device to local machine."""
    try:
        device = get_device(udid)
        output = device.pull_file(remote_path, local_path)
        console.print(f"[green]Pulled:[/green] {remote_path} → {output}")
        
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@files.command("push")
@click.argument("local_path")
@click.argument("remote_path")
@click.option("--udid", "-u", help="Device UDID")
def files_push(local_path: str, remote_path: str, udid: str):
    """Push a file from local machine to device."""
    try:
        device = get_device(udid)
        if device.push_file(local_path, remote_path):
            console.print(f"[green]Pushed:[/green] {local_path} → {remote_path}")
        else:
            console.print(f"[red]Failed to push file[/red]")
            raise SystemExit(1)
            
    except DeviceError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@main.command()
def tunnel():
    """Start tunnel daemon for iOS 17+ (requires sudo)."""
    console.print("[yellow]Starting tunnel daemon...[/yellow]")
    console.print("This requires sudo and will run in foreground.")
    console.print("Press Ctrl+C to stop.\n")
    
    import subprocess
    try:
        subprocess.run(
            ["sudo", "pymobiledevice3", "remote", "tunneld"],
            check=True
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Tunnel stopped.[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Tunnel failed:[/red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
