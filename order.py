class Order:
    def __init__(self, buying_price, created_at, amount_of_asset_bought):
        self.created_at = created_at
        self.buying_price = buying_price
        self.amount_of_asset_bought = amount_of_asset_bought
        self.selling_price = None
        self.executed_at = None

    def net_difference(self):
        return self.selling_price - self.buying_price

    def execute(self, selling_price, executed_at):
        self.selling_price = selling_price
        self.executed_at = executed_at
