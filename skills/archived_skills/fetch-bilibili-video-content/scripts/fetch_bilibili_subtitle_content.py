# /// script
# dependencies = [
#   "requests",
# ]
# ///

import re
import requests
import argparse

from config import BILIBILI_HEADERS

if not BILIBILI_HEADERS:
    print('请配置 BILIBILI_HEADERS，获取方法：通过网站 https://curlconverter.com/python/，自行把B站的curl命令转为python代码，将 headers 替换掉的 BILIBILI_HEADERS，注意把 cookie 键解除注释！')
    exit(1)


session = requests.Session()
session.headers.update(BILIBILI_HEADERS)


def fetch_bilibili_subtitles(video_url: str):
    """
    获取字幕列表（不含字幕正文）
    """

    if video_url.startswith('https://b23.tv/'):
        video_url = requests.get(video_url).url
        
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

        # print(f'B站视频: aid={aid}, cid={cid}')

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
        content_obj_list = data.get('body')
        return ", ".join([content_obj.get('content', '') for content_obj in content_obj_list])

    except Exception as e:
        print('B站字幕内容获取失败:', e)
        return []


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='获取B站视频字幕')
    
    # 添加视频URL参数
    parser.add_argument('VIDEO_URL', type=str, help='B站视频链接')
    
    # 添加可选参数：是否只获取字幕列表（不下载内容）
    parser.add_argument('--list-only', action='store_true', help='仅显示字幕信息列表，不获取内容')
    
    return parser.parse_args()


if __name__ == "__main__":
    # 获取命令行参数
    args = parse_arguments()
    video_url = args.VIDEO_URL
    # 检查是否只列出字幕
    if args.list_only:
        print(f"正在获取视频: {video_url} 的字幕列表...")
        subs = fetch_bilibili_subtitles(video_url)
        
        if subs:
            print(f"\n找到 {len(subs)} 个字幕:")
            for idx, sub in enumerate(subs):
                print(f"{idx + 1}. [{sub['lan_doc']}] ({'AI' if sub['isAI'] else 'CC'})")
                print(f"   ID: {sub['id']}, URL: {sub['subtitle_url']}")
        else:
            print("未找到字幕。您的 cookie 是否过期？")
        exit(0)

    content = f"以下是该B站视频的字幕内容：\n\n"
    subs = fetch_bilibili_subtitles(video_url)
    if not subs:
        print("未找到字幕，程序退出。您的 cookie 是否过期？")
        exit(1)

    # 寻找中英文字幕
    found = False
    for sub in subs:
        if sub['lan_doc'] == "中文" or sub['lan_doc'] == "English":
            content += fetch_bilibili_subtitle_content(sub['subtitle_url'])
            found = True
            break
    
    if not found:
        print("未找到中英文字幕，但找到了其他字幕，请使用 --list-only 参数查看。")
        exit(1)

    print(content)