# /// script
# dependencies = [
#   "zendriver",
#   "readability-lxml",
# ]
# ///

import argparse
import asyncio

import zendriver as zd
from readability import Document

import re
import html

def _strip_tags(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def _normalize(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r'[ \t]+', ' ', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def _to_markdown(html_content: str) -> str:
    """Convert HTML to markdown."""
    text = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                lambda m: f'[{_strip_tags(m[2])}]({m[1]})', html_content, flags=re.I)
    text = re.sub(r'<h([1-6])[^>]*>([\s\S]*?)</h\1>',
                lambda m: f'\n{"#" * int(m[1])} {_strip_tags(m[2])}\n', text, flags=re.I)
    text = re.sub(r'<li[^>]*>([\s\S]*?)</li>', lambda m: f'\n- {_strip_tags(m[1])}', text, flags=re.I)
    text = re.sub(r'</(p|div|section|article)>', '\n\n', text, flags=re.I)
    text = re.sub(r'<(br|hr)\s*/?>', '\n', text, flags=re.I)
    return _normalize(_strip_tags(text))

async def fetch_page_content(browser, url):
    """
    从指定URL的网页中提取标题和可读内容。

    功能说明:
        打开网页 → 等待加载 → 提取正文 → 用Readability解析 → 转为Markdown并提取文本 → 异常则返回默认值 → 关闭标签页。

    参数:
        browser (Browser): 浏览器实例，用于打开新标签页并操作网页。
        url (str): 要抓取的网页URL地址。

    返回:
        tuple: 包含三个元素的元组：
            - title (str): 页面标题，若提取失败则返回 "NO_TITLE"。
            - url (str): 原始URL，用于标识来源。
            - content (str): 提取后的文章正文内容，以纯文本形式呈现；若提取失败则返回 "NO_CONTENT"。

    示例:
        result = await fetch_page_content(browser, "https://example.com/article")
        title, url, content = result
        print(f"标题: {title}")
        print(f"内容: {content}")
    """

    try:
        tab = await browser.get(url, new_tab=True)
        await tab.sleep(10)
        await tab.select('body')
        content = await tab.get_content()

        # 使用 Readability-lxml 提取文章内容
        doc = Document(content)
        title = doc.title()
        content = _to_markdown(doc.summary())

        await tab.close()  # 可选：立即关闭 tab，节省资源
        return title, url, content
    except:
        return "NO_TITLE", url, "NO_CONTENT"
    
async def web_search(search_urls: list[str]) -> list[dict[str, str]]:
    """
    一个使代理能够基于用户查询进行网络搜索的工具，可快速访问最新的在线信息。
    你必须首先理解我的问题，然后重构成英文关键词来调用此工具。

    Args:
        english_query: English reconstructed keywords derived from my question.
    """

    try:
        browser = await zd.start(
            headless=True,
            browser_args=[
                "--disable-images",
                "--disable-fonts",
                "--disable-features=TranslateUI",
                "--disable-features=Translate"
            ]
        )
        # 并发获取所有页面内容
        tasks = [fetch_page_content(browser, url) for url in search_urls]
        results = await asyncio.gather(*tasks)

        # 打印结果
        results_list = []
        for title, url, content in results:
            if title == "NO_TITLE" or len(content) < 500:
                continue
            results_list.append({"title": title, "href": url, "body": content}) 

        return results_list
    
    except Exception as e:
        print(f"Error web searching: {str(e)}")
        return f"Error web searching: {str(e)}"
    
    finally:
        await browser.stop()

# 主函数：处理命令行参数并执行搜索
async def main():
    parser = argparse.ArgumentParser(description="Fetch and extract readable content from given URLs using a headless browser.")
    parser.add_argument("--url", action='append', type=str, help="A URL to fetch and extract content from (can be used multiple times)")
    args = parser.parse_args()

    # 执行搜索
    results = await web_search(args.url)
    print(results)

# 作为入口点运行
if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        print(f"❌ Unexpected error: {e}")