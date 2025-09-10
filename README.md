# 🤖 Telegram AI Assistant Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=brain&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

*A powerful multilingual Telegram bot built with Python that uses advanced AI capabilities to provide intelligent conversations, deep thinking analysis, web search, and customizable personality features.*

</div>

---
# 🚀 Download v1.0

👉 [Download Executable (Windows)](https://drive.google.com/file/d/1KSwA9Go9HTBDM6TB1zn55lTctw_jEEOD/view?usp=drivesdk)  
👉 [Download Source Code](https://drive.google.com/file/d/1H_TsrWGdzv7s18n9-R2R8FqQC5pHj4w7/view?usp=drivesdk)

## 🌟 Overview

This Telegram bot serves as an intelligent assistant with advanced natural language processing capabilities. It supports multiple languages, maintains conversation memory, offers deep analysis features, and allows users to customize the bot's personality. The bot uses the **g4f library** to provide AI-powered responses and includes comprehensive user statistics and server monitoring features.

## ✨ Features

### 🌍 **Core Capabilities**
- **Multilingual Support** - English, Spanish, French, Russian, and Arabic
- **Conversation Memory** - Remembers previous conversations for 2 days
- **Advanced Thinking Modes** - Deep analysis with multiple perspectives
- **Customizable Personality** - Change the bot's behavior and save presets

### 🔧 **Advanced Features**
- **Web Search** - Internet search across multiple reliable sources
- **User Statistics** - Track your usage and interaction history
- **Feedback System** - Share your opinions about the bot
- **Server Monitoring** - Real-time server performance information

### ⚙️ **System Features**
- **Preset System** - Save and load custom personality configurations
- **Automatic Cleanup** - Efficient memory management
- **Multi-format Support** - Source code and executable versions

---

## 🚀 Installation

### 📦 Option 1: Using Source Code

```bash
# 1. Download and extract telegram-bot-source-v1.0.zip
# 2. Navigate to the extracted directory

# 3. Create your token configuration
echo '{"token": "YOUR_TELEGRAM_BOT_TOKEN"}' > token.json

# 4. Run the bot
```

### 🎯 Option 2: Using Executable

```bash
# 1. Download and extract telegram-bot-exe-v1.0.zip
# 2. Navigate to the extracted directory

# 3. Create your token configuration
echo '{"token": "YOUR_TELEGRAM_BOT_TOKEN"}' > token.json

# 4. Run the executable
```

### 🔑 Getting a Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to name your bot
4. Copy the token provided by BotFather
5. Paste this token in your `token.json` file

---

## 📚 Usage

### 🎯 Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Start conversation and show help |
| `/help` | Show all available commands |
| `/clear` | Clear conversation memory |

### 🧠 Advanced Features

| Command | Description |
|---------|-------------|
| `/think [text]` | Deep thinking analysis on specific text |
| `/think_full` | Analyze last 10 messages |
| `/web [query]` | Search the internet |
| `/customize` | Customize bot personality |

### 📊 Statistics & Info

| Command | Description |
|---------|-------------|
| `/mystats` | Show your personal statistics |
| `/users_info` | General user statistics |
| `/server_info` | Server performance information |
| `/feedback` | Send feedback about the bot |
| `/credits` | Developer information |

### 🌐 Language Settings

| Command | Language |
|---------|----------|
| `/en` | English |
| `/sp` | Spanish |
| `/fr` | French |
| `/ru` | Russian |
| `/ar` | Arabic |

---

## ⚙️ Configuration

The bot uses several JSON files for data storage:

```
📁 Project Structure
├── 📄 token.json              # Bot authentication token
├── 📄 conversations.json      # User conversation data
├── 📄 user_stats.json         # User statistics
├── 📄 user_feedbacks.json     # User feedback data
├── 📄 bot_stats.json          # Bot performance statistics
└── 📄 telegram_bot.py         # Main bot script
```

### 📋 Configuration Example

```json
{
  "token": "1234567890:ABCdefGhIjKlMnOpQrStUvWxYz"
}
```

---

## 🛠️ Troubleshooting

### 🔧 Common Issues

**🚫 Bot doesn't start**
- Ensure your token is correctly formatted in `token.json`
- Check file permissions

**📡 No response from bot**
- Check your internet connection
- Verify the bot token is valid

**💾 Memory issues**
- The bot automatically cleans up old conversations
- Check available disk space

### 🐍 For Source Code Users

- Ensure you have **Python 3.7+** installed
- Run with administrative privileges if needed
- Install required dependencies: `Available in the Read Me file`

### 💻 For Executable Users

- The executable may be flagged by antivirus (false positive)
- Add exception for the executable if needed
- Ensure you have **.NET Framework** installed (if required)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

```bash
# 1. Fork the repository
git fork https://github.com/HAKORADev/telegram-ai-bot

# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Commit your changes
git commit -m 'Add amazing feature'

# 4. Push to the branch
git push origin feature/amazing-feature

# 5. Open a Pull Request
```

### 📝 Contribution Guidelines

- Follow Python PEP 8 style guide
- Add tests for new features
- Update documentation as needed
- Ensure compatibility with Python 3.7+

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 📞 Support

<div align="center">

**Need help? We've got you covered!**

[![Twitter](https://img.shields.io/badge/Twitter-@HAKORAdev-1DA1F2?style=for-the-badge&logo=twitter)](https://twitter.com/HAKORAdev)

</div>

For support and questions:
- 💬 **Contact**: Reach out via Twitter [@HAKORAdev](https://twitter.com/HAKORAdev)

---

## 🙏 Acknowledgments

- **🐍 Built with** [python-telegram-bot](https://python-telegram-bot.org/)
- **🤖 AI capabilities** powered by [g4f](https://github.com/xtekky/gpt4free)
- **🌍 Multilingual support** with custom translation system
- **🧠 Advanced conversation** processing and analysis features

---

## 📈 Version History

### 🎯 v1.0 (Current Release)
- ✅ Initial release
- ✅ Multilingual support (5 languages)
- ✅ Advanced thinking modes
- ✅ Customizable personality system
- ✅ Web search functionality
- ✅ Comprehensive user statistics
- ✅ Real-time server monitoring


## 🪙 Why This Bot?

| Self-hosted | Open-source | Zero API fees |
|-------------|-------------|---------------|
| Your server, your rules | MIT-licensed code | Runs on free g4f providers |


---

<div align="center">

**⚠️ Important Notice**

*After extracting either zip file, please read the included README file for complete installation and setup instructions specific to your version.*

---
# 🚀 Download v1.0

👉 [Download Executable (Windows)](https://drive.google.com/file/d/1KSwA9Go9HTBDM6TB1zn55lTctw_jEEOD/view?usp=drivesdk)  
👉 [Download Source Code](https://drive.google.com/file/d/1H_TsrWGdzv7s18n9-R2R8FqQC5pHj4w7/view?usp=drivesdk)

**Made with ❤️ by HAKORAdev**

⭐ **Star this repository if you found it helpful!** ⭐

</div>
