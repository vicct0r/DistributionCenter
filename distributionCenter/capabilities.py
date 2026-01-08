DESCRIPTION_MAP = {
    "buy_product": {
        "method": "GET",
        "path": "/cd/v1/product/buy/{product}/{quantity}/",
        "description": "Buy a given quantity of a product and update local inventory."
    },

    "sell_product": {
        "method": "GET",
        "path": "/cd/v1/product/sell/{product}/{quantity}/",
        "description": "Sell a given quantity of a product to a requesting CD."
    },

    "check_availability": {
        "method": "GET",
        "path": "/cd/v1/product/request/{product}/{quantity}/",
        "description": "Check whether the requested product is available in the given quantity."
    },
}
