# discord_pybot
### add this bot to your server ([click here](https://discord.com/api/oauth2/authorize?client_id=793388578880880660&permissions=8&scope=bot))
---

### **Features**:
##### Currently the bot can do following things:
- **print random quotes**
- **kick/ban a member**
- **Delete messages from certain channel**
- **play audio from youtube**

---
### **Installation**:

##### Download requirements from `requirements.txt` and you will also have to install `youtube-dl`. Follow steps given below to install `youtube-dl`

To install it right away for all UNIX users (Linux, macOS, etc.), type:

    sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
    sudo chmod a+rx /usr/local/bin/youtube-dl

Windows users can [download an .exe file](https://yt-dl.org/latest/youtube-dl.exe) and place it in any location on their [PATH](https://en.wikipedia.org/wiki/PATH_%28variable%29) except for `%SYSTEMROOT%\System32` (e.g. **do not** put in `C:\Windows\System32`).

macOS users can install youtube-dl with [Homebrew](https://brew.sh/):

    brew install youtube-dl

---

### **Usage**:
paste your bot's token here
```sh
client.run(os.environ['TOKEN'])
```

---
## © [Vandit](https://github.com/vendz)
