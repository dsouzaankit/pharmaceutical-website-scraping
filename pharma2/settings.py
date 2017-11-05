#Custom middleware must be after Redirect middleware in priority
DOWNLOADER_MIDDLEWARES = {
    'pharma2.middlewares.RandomUserAgentMiddleware': 80,
    'pharma2.middlewares.CustomMiddleware': 650,
}
