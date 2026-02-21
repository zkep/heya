from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from heya.core.logging import format_error_with_issue, get_logger

__all__ = ["WechatArticle", "WechatParser"]

logger = get_logger(__name__)


@dataclass
class WechatArticle:
    title: str
    url: str
    index: int = 0
    create_time: int = 0


class WechatParser:
    SINGLE_ARTICLE_PATTERN = re.compile(
        r"https?://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+"
    )
    PROFILE_PATTERN = re.compile(r"https?://mp\.weixin\.qq\.com/mp/profile_ext")
    ALBUM_PATTERN = re.compile(r"https?://mp\.weixin\.qq\.com/mp/appmsgalbum")
    BIZ_PATTERN = re.compile(r"__biz=([^&]+)")

    @staticmethod
    def is_wechat_url(url: str) -> bool:
        url = url.lower()
        return bool(
            WechatParser.SINGLE_ARTICLE_PATTERN.match(url)
            or WechatParser.PROFILE_PATTERN.match(url)
            or WechatParser.ALBUM_PATTERN.match(url)
            or "mp.weixin.qq.com" in url
        )

    @staticmethod
    def is_article_list(url: str) -> bool:
        url = url.lower()
        return bool(
            WechatParser.PROFILE_PATTERN.match(url)
            or WechatParser.ALBUM_PATTERN.match(url)
            or "/mp/profile_ext" in url
            or "/mp/appmsgalbum" in url
        )

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize WeChat URL to handle different formats"""
        # Remove fragment identifiers
        if "#" in url:
            url = url.split("#")[0]
        # Remove trailing slashes
        url = url.rstrip("/")
        return url

    @staticmethod
    async def parse_article_list(url: str) -> list[WechatArticle]:
        normalized_url = WechatParser.normalize_url(url)
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(normalized_url, timeout=30000, wait_until="networkidle")
                await page.wait_for_timeout(2000)

                if "/appmsgalbum" in normalized_url:
                    await WechatParser._scroll_to_load_all_articles(page)

                articles = await WechatParser._extract_articles_from_page(page)
                await browser.close()

                if articles:
                    for idx, article in enumerate(articles):
                        article.index = idx + 1

                return articles
        except Exception as e:
            raise Exception(format_error_with_issue(e)) from e

    @staticmethod
    async def _scroll_to_load_all_articles(page: Any) -> None:
        last_height = 0
        max_scrolls = 10
        scroll_count = 0
        stable_count = 0
        max_stable = 2

        while scroll_count < max_scrolls and stable_count < max_stable:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)

            current_height = await page.evaluate("document.body.scrollHeight")

            if current_height == last_height:
                stable_count += 1
            else:
                stable_count = 0
                last_height = current_height

            scroll_count += 1

        try:
            cgi_data = await page.evaluate("window.cgiData")
            if cgi_data and cgi_data.get("continue_flag") == 1:
                for i in range(3):
                    scroll_position = (i + 1) * 8000
                    await page.evaluate(f"window.scrollTo(0, {scroll_position})")
                    await page.wait_for_timeout(1500)

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
        except Exception:
            pass

    @staticmethod
    async def _extract_articles_from_page(page: Any) -> list[WechatArticle]:
        selector_strategies = [
            WechatParser._try_extract_by_profile_selector,
            WechatParser._try_extract_by_js_title_selector,
            WechatParser._try_extract_by_album_selector,
            WechatParser._try_extract_by_appmsg_selector,
            WechatParser._try_extract_by_link_selector,
            WechatParser._try_extract_by_appmsg_link,
            WechatParser._try_extract_by_card_selector,
            WechatParser._try_extract_by_list_selector,
            WechatParser._try_extract_by_general_selector,
            WechatParser._try_extract_by_cgi_data,
        ]

        for strategy in selector_strategies:
            articles = await strategy(page)
            if articles:
                return articles

        return []

    @staticmethod
    async def _try_extract_by_profile_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("a.weui_media_appmsg")
            for idx, elem in enumerate(article_elements):
                title_elem = await elem.query_selector("h4.weui_media_title")
                title = await title_elem.inner_text() if title_elem else f"Article {idx + 1}"
                url = await elem.get_attribute("href")
                if url:
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_js_title_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("a.js_title")
            for idx, elem in enumerate(article_elements):
                title = await elem.inner_text() or f"Article {idx + 1}"
                url = await elem.get_attribute("href")
                if url:
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_link_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("a[href*='/s/']")
            for idx, elem in enumerate(article_elements):
                title = await elem.inner_text() or f"Article {idx + 1}"
                url = await elem.get_attribute("href")
                if url and "/s/" in url:
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_album_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("div[data-sku*='appmsgalbum'] a")
            for idx, elem in enumerate(article_elements):
                url = await elem.get_attribute("href")
                if url and "/s/" in url:
                    title = await elem.inner_text() or f"Article {idx + 1}"
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_general_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("a")
            for idx, elem in enumerate(article_elements):
                url = await elem.get_attribute("href")
                if url and "/s/" in url:
                    title = await elem.inner_text() or f"Article {idx + 1}"
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_appmsg_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("div.appmsg_item a")
            for idx, elem in enumerate(article_elements):
                title_elem = await elem.query_selector("h3.appmsg_title")
                title = await title_elem.inner_text() if title_elem else f"Article {idx + 1}"
                url = await elem.get_attribute("href")
                if url:
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_appmsg_link(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("a.appmsg-link")
            for idx, elem in enumerate(article_elements):
                title = await elem.inner_text() or f"Article {idx + 1}"
                url = await elem.get_attribute("href")
                if url:
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_card_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("div.card-wrap a")
            for idx, elem in enumerate(article_elements):
                url = await elem.get_attribute("href")
                if url and "/s/" in url:
                    title_elem = (
                        await elem.query_selector("h4")
                        or await elem.query_selector("h3")
                        or await elem.query_selector("h2")
                    )
                    title = (
                        await title_elem.inner_text() if title_elem else f"Article {idx + 1}"
                    )
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_list_selector(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        try:
            article_elements = await page.query_selector_all("ul.appmsg-list li a")
            for idx, elem in enumerate(article_elements):
                url = await elem.get_attribute("href")
                if url and "/s/" in url:
                    title = await elem.inner_text() or f"Article {idx + 1}"
                    articles.append(WechatArticle(title=title, url=url, index=idx + 1))
        except Exception:
            pass
        return articles

    @staticmethod
    async def _try_extract_by_cgi_data(page: Any) -> list[WechatArticle]:
        articles: list[WechatArticle] = []
        if "/appmsgalbum" not in page.url:
            return articles

        try:
            cgi_data = await page.evaluate("window.cgiData")
            article_list = None
            if cgi_data:
                if "articleList" in cgi_data:
                    article_list = cgi_data["articleList"]
                elif "list" in cgi_data:
                    article_list = cgi_data["list"]

            if article_list:
                for idx, item in enumerate(article_list):
                    if "url" in item and "title" in item:
                        url = item["url"]
                        title = item["title"]
                        create_time = item.get("create_time", 0)
                        url = url.replace("&amp;", "&")
                        if url and "/s" in url:
                            articles.append(
                                WechatArticle(
                                    title=title,
                                    url=url,
                                    index=idx + 1,
                                    create_time=create_time,
                                )
                            )

            if cgi_data and cgi_data.get("continue_flag") == 1:
                articles = await WechatParser._fetch_more_articles(page, cgi_data, articles)
        except Exception:
            pass

        return articles

    @staticmethod
    async def _fetch_more_articles(
        page: Any, cgi_data: dict, articles: list[WechatArticle]
    ) -> list[WechatArticle]:
        total_articles = cgi_data.get("article_count", len(articles))
        max_pages = 5
        page_count = 0
        article_list = cgi_data.get("articleList", cgi_data.get("list", []))

        while len(articles) < total_articles and page_count < max_pages:
            if articles and article_list:
                last_article = article_list[-1]
                last_msgid = last_article.get("msgid")
                last_itemidx = last_article.get("itemidx")

                if last_msgid and last_itemidx:
                    import urllib.parse

                    parsed_url = urllib.parse.urlparse(page.url)
                    params = dict(urllib.parse.parse_qsl(parsed_url.query))

                    params["begin_msgid"] = last_msgid
                    params["begin_itemidx"] = last_itemidx

                    pagination_url = urllib.parse.urlunparse(
                        (
                            parsed_url.scheme,
                            parsed_url.netloc,
                            parsed_url.path,
                            parsed_url.params,
                            urllib.parse.urlencode(params),
                            parsed_url.fragment,
                        )
                    )

                    await page.goto(pagination_url, timeout=30000, wait_until="networkidle")
                    await page.wait_for_timeout(3000)

                    updated_cgi_data = await page.evaluate("window.cgiData")
                    if updated_cgi_data and "articleList" in updated_cgi_data:
                        more_articles = updated_cgi_data["articleList"]

                        start_idx = len(articles) + 1
                        for idx, item in enumerate(more_articles):
                            if "url" in item and "title" in item:
                                url = item["url"]
                                title = item["title"]
                                create_time = item.get("create_time", 0)
                                url = url.replace("&amp;", "&")
                                if url and "/s" in url:
                                    articles.append(
                                        WechatArticle(
                                            title=title,
                                            url=url,
                                            index=start_idx + idx,
                                            create_time=create_time,
                                        )
                                    )

                        article_list = more_articles

                        if not updated_cgi_data.get("continue_flag") == 1:
                            break

                        cgi_data = updated_cgi_data
                    else:
                        break
                else:
                    break

            page_count += 1
            await page.wait_for_timeout(1000)

        return articles
