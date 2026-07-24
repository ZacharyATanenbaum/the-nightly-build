from nb_web.common import normalize_url, primary_hint


def test_bing_news_redirect_unwraps_to_the_https_publisher_url():
    wrapped = (
        "http://www.bing.com/news/apiclick.aspx?ref=FexRss&aid=&tid=abc123"
        "&url=https%3A%2F%2Fgizmodo.com%2Fchatgpt-health-rolls-out-to-everyone-2000789999"
        "&c=123&mkt=en-us"
    )

    assert normalize_url(wrapped) == (
        "https://gizmodo.com/chatgpt-health-rolls-out-to-everyone-2000789999"
    )


def test_normalized_sources_are_https_and_drop_tracking_parameters():
    assert normalize_url(
        "http://example.com/report?utm_source=rss&item=1#fragment"
    ) == "https://example.com/report?item=1"


def test_unwrapped_publisher_is_classified_by_its_own_domain():
    wrapped = (
        "https://www.bing.com/news/apiclick.aspx?"
        "url=https%3A%2F%2Fopenai.com%2Findex%2Fhealth-in-chatgpt"
    )
    unwrapped = normalize_url(wrapped)

    assert unwrapped == "https://openai.com/index/health-in-chatgpt"
    assert primary_hint(unwrapped) == "primary"
