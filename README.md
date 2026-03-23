# FoxESS Cloud for Home Assistant

Custom Home Assistant integration that queries the FoxESS Cloud API and exposes inverter data as sensor entities.

## What This Integration Does

- Provides setup through the Home Assistant UI (`Config Flow`)
- Validates the API key during configuration
- Creates sensors for inverter status, generation, consumption, and electrical values
- Automatically detects the number of available PV inputs on the device
- Periodically refreshes data from the FoxESS cloud

## Requirements

- A valid FoxESS Cloud API key
- The device serial number

## Installation

At the moment, the installation method is manual.

1. Copy the `custom_components/foxess_cloud` folder into the `config/custom_components/` directory of your Home Assistant installation.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **FoxESS Cloud**.

## Configuration

When adding the integration, the setup asks for:

- `API Key`: FoxESS Cloud API access key
- `Device SN`: inverter or device serial number
- `Device Name`: friendly name shown in Home Assistant

## Update Frequency

The integration coordinator runs on a 1-minute cycle, with separate internal refresh windows for each data group:

- Device details: approximately every 15 minutes
- Generation data: approximately every 5 minutes
- Real-time data: approximately every 2 minutes

## Current Limitations

- The integration currently doesn't expose battery information
- There are currently no repository-specific HACS installation instructions
- The project is still in alpha