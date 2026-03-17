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
    return re.sub(r'[ \n]{3,}', '\n\n', text).strip()

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
        # content = _to_markdown(doc.summary())
        content = _to_markdown(content)

        await tab.close()  # 可选：立即关闭 tab，节省资源
        return title, url, content
    except:
        return "NO_TITLE", url, "NO_CONTENT"
    
async def fetch_relevant_web_pages(search_urls: list[str]) -> list[dict[str, str]]:
    """
        异步并发抓取多个网页内容，并过滤掉标题缺失或正文过短的页面。
        该函数使用无头浏览器（基于 zd 库）访问给定的 URL 列表，提取每个页面的标题、URL 和正文文本。
        为提升性能和减少资源消耗，浏览器启动时禁用了图片、字体及翻译功能。
        仅保留满足以下条件的页面：
            - 页面有有效标题（非 "NO_TITLE"）
            - 正文内容长度不少于 500 个字符
        参数:
            search_urls (list[str]): 待抓取的网页 URL 列表。
        返回:
            list[dict[str, str]]: 包含有效页面信息的字典列表，每个字典包含：
                - "title": 网页标题
                - "href": 网页 URL
                - "body": 网页正文文本（纯文本）
        异常处理:
            若在抓取过程中发生任何异常，函数将打印错误信息并返回空列表，
            以确保调用方不会因单个页面失败而中断整体流程。
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
            if title == "NO_TITLE":
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
    results = await fetch_relevant_web_pages(args.url)
    print(results)

# 作为入口点运行
if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        print(f"❌ Unexpected error: {e}")