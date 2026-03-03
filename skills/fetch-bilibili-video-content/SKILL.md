---
name: fetch-bilibili-video-content
description: 本技能用于获取指定 Bilibili 视频的文本内容，支持：获取视频完整的文本内容
---

# Fetch Bilibili Subtitle Content SKILL

## Available scripts

- **`scripts/fetch_bilibili_subtitle_content.py`** — 获取指定 Bilibili 视频的文本内容

## Usage

### `fetch_bilibili_subtitle_content.py`

usage: fetch_bilibili_subtitle_content.py [-h] [--list-only] VIDEO_URL

获取B站视频字幕

positional arguments:
  VIDEO_URL    B站视频链接

options:
  -h, --help   show this help message and exit
  --list-only  仅显示字幕信息列表，不获取内容

## Examples

### 1. 获取完整视频文本内容

```bash
uv run scripts/fetch_bilibili_subtitle_content.py "https://www.bilibili.com/video/BV1xxxxxxx"
```

或者

```bash
uv run scripts/fetch_bilibili_subtitle_content.py "https://b23.tv/2AS8WG5"
```
