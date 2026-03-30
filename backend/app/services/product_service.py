from app.models.product import ProductOverview


def get_product_overview() -> ProductOverview:
    return ProductOverview(
        platform="AI Market-Intelligence Platform",
        api_products=[
            "POST /api/v1/intelligence/analyze-event",
            "POST /api/v1/intelligence/generate-signal",
            "POST /api/v1/intelligence/send-alert",
        ],
        trader_app_features=[
            "Live explainable signal cards",
            "Watchlist-focused alerts",
            "Confidence and risk overlays",
        ],
        core_modules=[
            "Ingestion",
            "NLP + Impact engine",
            "Signal engine",
            "Risk engine",
            "Alert delivery",
            "API + billing + auth",
            "Monitoring + audit + compliance",
        ],
        business_value=[
            "Saves users time",
            "Filters noise",
            "Provides faster actionable market insight",
            "Scales as global API + SaaS",
        ],
    )
