# 🌤️ FoxESS Cloud for Home Assistant

A custom [Home Assistant](https://www.home-assistant.io) integration that connects to the **FoxESS Cloud API** to fetch inverter data and expose it as sensor entities ⚡.

This integration uses the **modern UI Flow**, which simplifies the configuration process, requires **no restarts**, and groups sensor entities into **area-capable devices** 🧩.

## ⚙️ Installation

### 📦 Manual Installation

1. Copy the contents of `custom_components/foxess_cloud` to:  
   `/config/custom_components/foxess_cloud`
2. Restart Home Assistant.

## 🔧 Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **FoxESS Cloud**
3. Enter the following information:

   - **API Key** 🗝️
     Log in to [FoxESS Cloud](https://www.foxesscloud.com/), click your **User Icon → User Profile → API Management → Private Token**, then click **Generate API Key**.

   - **Device SN** 🔢
     The serial number of your inverter.

   - **Device Name** 🏷️
     An optional name to identify this device in Home Assistant.

## ⏱️ Update Frequency

This integration updates data automatically with different refresh intervals per group:

| Data Group       | Refresh Interval |
|------------------|------------------|
| Device details   | ~15 minutes      |
| Generation data  | ~5 minutes       |
| Real-time data   | ~2 minutes       |


## 🧩 Entities Provided

The integration exposes the following entities (depending on inverter model):

`TODO`

## ⚠️ Current Limitations

- 🚧 The project is still in **alpha stage**  
- Requires an **active FoxESS Cloud account** with generated API key

## ❤️ Contribute

Issues and pull requests are welcome!  

### 🌐 Links
- 🏠 [Home Assistant](https://www.home-assistant.io)
- ☁️ [FoxESS Cloud](https://www.foxesscloud.com/)
