"""
Bilibili 字幕获取脚本（单文件执行版）

功能说明：
    本脚本用于从 Bilibili 视频页面自动获取字幕列表及字幕正文内容，支持中英等多种语言字幕（含 AI 生成与人工字幕），并可逐条解析字幕文本内容。

使用场景：
    - 自动获取视频字幕（文本格式）
    - 用于视频字幕分析、翻译、存档等任务
    - 适用于研究、学习、内容创作等场景

📌 注意事项：
    1. 本脚本需通过浏览器开发者工具获取原始请求的 headers 和 cookies。
    2. cookie 字段必须正确配置，否则请求将被拒绝。
    3. 请确保网络环境可访问 Bilibili API 接口（需稳定连接）。
    4. 本脚本不涉及视频下载，仅用于字幕信息提取。
    5. 若视频无字幕或字幕权限受限，将返回空列表或错误提示。

🔧 使用方法：
    1. 打开浏览器，访问目标 Bilibili 视频页面（如：https://www.bilibili.com/video/BVxxx/）
    2. 按 F12 打开开发者工具，进入 Network 标签页
    3. 刷新页面，找到请求路径为：
    - https://www.bilibili.com/
    4. 右键点击任一请求 → 复制 → 使用 https://curlconverter.com/python/ 将 curl 命令转换为 Python 代码
    5. 将转换后的 headers 中的 'cookie' 字段取消注释并填写真实值（如：_bili_jid=xxx; ...）
    6. 将转换后的 headers 代码替换脚本中对应位置
    7. 修改 video_url 变量为你要解析的视频地址
    8. 保存为 .py 文件并运行即可

📌 脚本结构与流程：
    1. 初始化 requests 会话，设置 headers 和 cookies
    2. 解析视频 URL 获取 bvid 和 page（页码）
    3. 通过 API 获取视频基础信息（aid, cid, pages）
    4. 从 player 接口获取字幕列表（subtitles）
    5. 遍历每个字幕项，提取语言标签（lan）、说明（lan_doc）、URL
    6. 对每个字幕 URL 发起请求，获取字幕正文内容（body）
    7. 输出字幕语言、URL、条数与正文内容

📌 输出示例：
    中文 (CN) https://xxx.com/subtitle/123
    字幕条数: 10
    ['00:00:01.000 --> 00:00:05.000', '这是第一条字幕...', ...]

⚠️ 风险提示：
    - 本脚本不涉及版权内容，仅用于个人学习与非商业用途
    - 若频繁调用 API，可能触发反爬机制，请合理控制频率
    - Bilibili 会定期更新 API 或加密逻辑，本脚本可能随版本迭代失效

🔧 依赖库：
    - requests：用于 HTTP 请求
    - re：用于 URL 解析

💡 建议后续扩展：
    - 支持将字幕内容保存为 SRT 或 TXT 文件
    - 增加语言识别与自动翻译功能
    - 添加缓存机制避免重复请求
    - 支持批量处理多个视频
"""

# === 自己需要修改的变量 ===

video_url = "https://www.bilibili.com/video/BVxxx/"

# 通过网站 https://curlconverter.com/python/，自行把curl命令转为python代码，将其中的headers复制过来，注意要把cookie键解除注释！
headers = {
    'accept': 'xxx',
    'accept-language': 'xxx',
    'cache-control': 'xxx',
    'priority': 'xxx',
    'sec-ch-ua': 'xxx',
    'sec-fetch-dest': 'xxx',
    'sec-fetch-mode': 'xxx',
    'sec-fetch-site': 'xxx',
    'sec-fetch-user': 'xxx',
    'upgrade-insecure-requests': 'xxx',
    'user-agent': 'xxx',
    'cookie': 'xxx',
}

# === 自己需要修改的变量 ===

import re
import requests

session = requests.Session()
session.headers.update(headers)


def fetch_bilibili_subtitles(video_url: str):
    """
    获取字幕列表（不含字幕正文）
    """
    bvid_match = re.search(r'(BV[\w]+)', video_url)
    page_match = re.search(r'[?&]p=(\d+)', video_url)

    bvid = bvid_match.group(1) if bvid_match else None
    page = int(page_match.group(1)) if page_match else 1

    if not bvid:
        print('无法获取 bvid')
        return []

    try:
        # 获取 aid / cid
        view_resp = session.get(
            'https://api.bilibili.com/x/web-interface/view',
            params={'bvid': bvid},
            cookies=session.cookies
        )
        view_data = view_resp.json()

        if view_data.get('code') != 0 or not view_data.get('data'):
            print('获取视频信息失败:', view_data.get('message'))
            return []

        data = view_data['data']
        aid = data['aid']
        pages = data.get('pages', [])
        cid = data.get('cid')

        if len(pages) >= page:
            cid = pages[page - 1]['cid']

        print(f'B站视频: aid={aid}, cid={cid}')

        # 获取字幕列表
        player_resp = session.get(
            'https://api.bilibili.com/x/player/wbi/v2',
            params={'aid': aid, 'cid': cid},
            cookies=session.cookies
        )
        player_data = player_resp.json()

        subtitles = (
            player_data
            .get('data', {})
            .get('subtitle', {})
            .get('subtitles')
        )

        if not subtitles:
            print('获取字幕列表失败')
            return []

        result = []
        for idx, sub in enumerate(subtitles):
            lan = sub.get('lan', '')
            result.append({
                'id': sub.get('id', idx),
                'lan': lan,
                'lan_doc': sub.get('lan_doc'),
                'subtitle_url': sub.get('subtitle_url'),
                'isAI': lan.startswith('ai-'),
                'isCC': not lan.startswith('ai-'),
                'isAuto': False,
                'body': None
            })

        return result

    except Exception as e:
        print('B站字幕获取出错:', e)
        return []


def fetch_bilibili_subtitle_content(url: str):
    """
    获取单条字幕正文
    """
    try:
        if url.startswith('//'):
            url = 'https:' + url

        resp = session.get(url)
        data = resp.json()
        return data.get('body', [])

    except Exception as e:
        print('B站字幕内容获取失败:', e)
        return []


subs = fetch_bilibili_subtitles(video_url)
for sub in subs:
    print(sub['lan_doc'], sub['subtitle_url'])
    content = fetch_bilibili_subtitle_content(sub['subtitle_url'])
    print('字幕条数:', len(content))
    print(content)

