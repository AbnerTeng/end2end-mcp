import mcp.types as types


PROMPTS = {
    "analyze-csv": types.Prompt(
        name="analyze-csv",
        description="Analyzes a CSV file containing stock trading info",
        arguments=[
            types.PromptArgument(
                name="csv_path",
                description="Path to the local CSV file",
                required=True,
            )
        ],
    ),
    "trade": types.Prompt(
        name="trade",
        description="Places a long order for a stock at a specific price and quantity",
        arguments=[
            types.PromptArgument(
                name="stock_id",
                description="Stock ID",
                required=True,
            ),
            types.PromptArgument(
                name="price",
                description="Price",
                required=True,
            ),
            types.PromptArgument(
                name="quantity",
                description="Quantity (number of shares)",
                required=True,
            ),
        ],
    ),
}
