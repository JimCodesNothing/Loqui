
# 🎯 Cold Approach Tracker

A comprehensive, gamified web application designed to track, analyse, and optimise your cold outreach efforts. Built with Python and Streamlit, it features automatic cloud synchronisation, advanced analytics, and satisfying audio feedback to keep you motivated.

## ✨ Features

- **📝 Detailed Logging**: Track Date, Time, Name, Location, Method, Result, Notes, and Follow-up dates.
- **🏆 Gamification System**: 
  - 🔥 Daily streak tracking (current and best).
  - 🏅 13 unlockable achievements (e.g., "First Win", "Week Warrior", "Night Owl").
  - 🎯 Customizable monthly challenges with progress bars and celebration effects.
- **📊 Advanced Analytics**: 
  - Success rates and method breakdowns.
  - Hourly performance trends.
  - Location performance heatmaps.
  - Conversion funnels.
- **☁️ Multi-Device Cloud Sync**: Optional integration with Google Sheets so your data persists across phones, tablets, and computers.
- **🔊 Audio Feedback**: Satisfying Web Audio API chimes when logging approaches, unlocking achievements, or completing challenges.
- **📱 Mobile-Ready**: Fully responsive design. Can be installed as a Progressive Web App (PWA) on iOS and Android home screens.
- **🔒 Multi-User Support**: Simple login system to keep different users' data isolated within the same Google Sheet.

## 🛠️ Tech Stack

- **Frontend/Backend**: Python, Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly, Streamlit native charts
- **Cloud Storage**: Google Sheets API (`gspread`, `oauth2client`)

## 🚀 Quick Start (Local Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JimCodesNothing/cold-approach-tracker.git
   cd cold-approach-tracker
   ```
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app**:
   ```bash
   streamlit run app.py
   ```
   *Note: Local runs will use browser session storage. To enable Google Sheets sync locally, you must create a `.streamlit/secrets.toml` file with your credentials.*

## ☁️ Deployment (Streamlit Community Cloud)

This app is designed to be deployed for **free** on [Streamlit Community Cloud](https://share.streamlit.io/).

1. Fork or push this repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app** and select this repository, the `main` branch, and `app.py` as the main file.
4. **Crucial Step (Google Sheets Sync)**: 
   - In your Streamlit app dashboard, go to **Settings** → **Secrets**.
   - Add your Google Cloud Service Account credentials in TOML format (see `secrets.toml.example` or deployment docs).
   - *Do NOT commit your JSON credentials file to this public repository.*
5. Click **Deploy!**

## 📱 Install as a Mobile App (PWA)

- **iOS (Safari)**: Open the Streamlit URL → Tap the Share icon → Scroll down → Tap **"Add to Home Screen"**.
- **Android (Chrome)**: Open the Streamlit URL → Tap the three dots (⋮) → Tap **"Install app"** or **"Add to Home screen"**.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
*Built to help you track every approach, analyse what works, and close more deals.* 🚀
```
