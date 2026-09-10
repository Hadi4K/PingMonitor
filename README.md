# Ping Monitor

A lightweight real-time network latency monitor for Windows.

Ping Monitor provides a simple desktop interface for monitoring network latency, packet loss, and connectivity in real time.

## Features

* Real-time ping monitoring
* Live latency display
* Packet loss tracking
* Live ping log
* Public IP detection
* Built-in network targets
* Custom IP address support
* Start / Stop monitoring
* Windows native ping
* Lightweight desktop interface
* Portable Windows version
* No installation required for the portable release

## Built-in Targets

The application includes several predefined targets:

* Google DNS
* Cloudflare DNS
* Quad9 DNS
* OpenDNS
* MyTeamSpeak
* Soft98
* Minecraft Server
* CS2 Server

You can also enter your own IP address or hostname.

## Requirements

### Portable Version

The portable release does not require Python to be installed.

Supported operating systems:

* Windows 10
* Windows 11

### Running From Source

Python 3.14+ is recommended.

Install the required dependency:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python main.py
```

## Download

The latest portable Windows version is available from the project's Releases page.

No installer is required.

Download the ZIP, extract it, and run:

```text
Ping Monitor.exe
```

## Screenshots

![Ping Monitor](screenshots/main.png)

## Building

The project uses PyInstaller to create the Windows executable.

Run:

```text
build_release.bat
```

The generated files are placed in the `dist` directory.

## Project Structure

```text
PingMonitor/
├── .github/
│   └── workflows/
│       └── build.yml
├── main.py
├── PingMonitor.ico
├── build_release.bat
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Version

Current version: **1.0.0**

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
