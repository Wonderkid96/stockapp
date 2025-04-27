class RiskManager:
    def __init__(self, account_balance, cfg):
        self.balance = account_balance
        self.daily_loss_limit = cfg["account"]["max_daily_loss_pct"] / 100 * account_balance
        self.loss_today = 0
        self.max_per_trade = cfg["account"]["risk_per_trade_pct"] / 100 * account_balance

    def record_pl(self, pl):
        self.loss_today += max(-pl, 0)
        if self.loss_today >= self.daily_loss_limit:
            raise Exception("Daily loss limit reached")

    def position_size(self, stop_risk_amount):
        # risk per trade cap
        return min(self.max_per_trade, stop_risk_amount) 