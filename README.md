# URL2MP3

A lightweight desktop application for downloading and converting audio from online media links.

## Features

- **Multi-Platform Support**: Download audio from YouTube, YouTube Music, and other supported platforms
- **Batch Downloads**: Process multiple URLs simultaneously
- **Format Options**: Convert to MP3, M4A, OPUS, WAV, or FLAC
- **Quality Selection**: Choose from multiple bitrate options (128, 192, 256, 320 kbps)
- **Metadata Embedding**: Automatically embed track metadata and thumbnails
- **Progress Tracking**: Real-time progress for individual and overall downloads
- **Status Display**: Clear indication of pending, downloading, converting, completed, and error states
- **Persistent Settings**: Remembers your last-used output directory and preferences
- **User-Friendly GUI**: Clean and simple Tkinter interface
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7 or higher
- FFmpeg (must be installed and available in system PATH)
- yt-dlp (installed via pip)

## Installation

### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

### 2. Install FFmpeg

**Windows:**
- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract and add to system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Debian/Ubuntu
sudo yum install ffmpeg      # CentOS/RHEL
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install yt-dlp
```

## Usage

### Running the Application

```bash
python url2mp3.py
```

### Using the GUI

1. **Enter URLs**: Paste one or more media URLs in the text area (one per line for batch downloads)
2. **Select Output Folder**: Click "Browse..." to choose where to save downloaded files
3. **Choose Format**: Select your preferred audio format (MP3, M4A, OPUS, WAV, FLAC)
4. **Set Bitrate**: Choose audio quality in kbps (128, 192, 256, 320)
5. **Optional Settings**:
   - Check "Embed metadata" to include track information
   - Check "Embed thumbnail as cover art" to add album artwork
6. **Start Download**: Click "Start Download" button
7. **Monitor Progress**: Watch individual download status and overall progress
8. **Cancel if Needed**: Click "Cancel" to stop ongoing downloads

### Status Indicators

- **Pending**: URL is queued for download
- **Downloading**: Actively downloading audio
- **Converting**: Processing and converting audio file
- **Completed**: Successfully downloaded and converted
- **Error**: Download or conversion failed

## Supported Platforms

Thanks to yt-dlp, URL2MP3 supports hundreds of sites, including:
- YouTube
- YouTube Music
- SoundCloud
- Vimeo
- And many more...

For a complete list, see [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## Configuration

The application automatically saves your preferences to `~/.url2mp3_config.json`:
- Last used output folder
- Preferred audio format
- Preferred bitrate
- Metadata embedding preference
- Thumbnail embedding preference

## Troubleshooting

### "FFmpeg not found" error
Ensure FFmpeg is installed and available in your system PATH. Test by running `ffmpeg -version` in your terminal.

### Download fails with "Unable to extract"
The URL may not be supported or the video may be restricted. Try a different URL or check if the video is accessible in your region.

### Slow download speeds
This depends on your internet connection and the source server. The application downloads at the maximum speed allowed by both.

### No audio output
Ensure the selected bitrate is compatible with your chosen format. Some formats have limitations on maximum bitrate.

## Development

### Project Structure
- `url2mp3.py` - Main application with GUI and download logic
- `requirements.txt` - Python dependencies
- `README.md` - Documentation

### Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available under the MIT License.

## Credits

Built with:
- [Python](https://www.python.org/) - Programming language
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Media downloading library
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework

## Disclaimer

This tool is for personal use only. Please respect copyright laws and terms of service of the platforms you download from. Only download content you have the right to access.
