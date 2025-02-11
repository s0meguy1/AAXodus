# AAXodus

**Because your audio deserves freedom.**  

Welcome to **AAXodus**, a simple script that extracts activation bytes from Audible and helps convert your AAX audiobooks to MP3. This project is a fork/continuation of code originally found here: [inAudible-NG/audible-activator](https://github.com/inAudible-NG/audible-activator). The original repo hasn’t been updated in a while, so I decided to pick up the torch and keep it working with the latest dependencies.

---

## Why “AAXodus”?

The name comes from the concept of freeing your audiobooks from the locked AAX format. Think of it as an exodus from any proprietary constraints—hence **AAX** + **exodus** = **AAXodus**. 

---

## Credit

- The **audible-activator.py** file is taken (with minimal modifications) from the original [inAudible-NG/audible-activator](https://github.com/inAudible-NG/audible-activator).  
- Full credit to them for the groundwork. I’ve only updated it to ensure compatibility with modern dependencies and browsers.

---

## How It Works

1. **Grab Activation Bytes**:  
   - The script uses Selenium to log into your Audible account, then retrieves your unique activation bytes.  
   - Activation bytes are needed by `ffmpeg` to correctly decode the .aax file.

2. **Convert to MP3 (via FFmpeg)**:  
   - Once you have your activation bytes, you can simply run `ffmpeg` like so:
     ```bash
     ffmpeg -activation_bytes ACTIVATION_BYTES -i input.aax -vn -c:a libmp3lame -q:a 4 output.mp3
     ```
   - The `-q:a 4` flag sets a good quality for MP3 encoding. You can adjust as you see fit.

---

## Installation & Usage

### 1. Install Dependencies
- **Python 3** (Tested with Python 3+)
- **pip** or a similar Python package manager
- **Chrome** or **Firefox** browser
- **ChromeDriver** or **GeckoDriver** (Automatically handled by `webdriver-manager` in this updated script)
- **ffmpeg** (for converting AAX to MP3)

### 2. Clone the Repo
```bash
git clone https://github.com/yourusername/AAXodus.git
cd AAXodus
```

### 3. Install Python Requirements
```bash
pip install -r requirements.txt
```
*(Ensure you also have Selenium and webdriver-manager installed.)*

### 4. Run the Script
```bash
python audible-activator.py --username YOUR_AUDIBLE_EMAIL --password YOUR_AUDIBLE_PASSWORD
```
- This will launch a browser window, log you in to Audible, and generate the `activation_bytes` printed in the terminal and stored in an `activation.blob` file.

### 5. Convert Your .aax to .mp3
```bash
ffmpeg -activation_bytes ACTIVATION_BYTES \
       -i input.aax \
       -vn -c:a libmp3lame -q:a 4 \
       output.mp3
```

---

## Disclaimer

- **AAXodus** is provided for legal, personal use of content you’ve purchased.  
- If you do not own the rights to the content, do not use this tool for any illegal purposes.  
- I am not responsible for how you use this tool. Always comply with your local laws regarding audio conversions.

---

Happy converting! If you have any questions, feel free to open an issue or submit a pull request.  
**Long live the audio freedom!**  
