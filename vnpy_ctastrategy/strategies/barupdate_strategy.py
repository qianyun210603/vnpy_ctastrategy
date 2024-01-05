from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class BarupdateStrategy(CtaTemplate):
    author = "Cui"

    f15min_open = 0.0
    f15min_high = 0.0
    f15min_low = 0.0
    f15min_close = 0.0

    f5min_open = 0.0
    f5min_high = 0.0
    f5min_low = 0.0
    f5min_close = 0.0

    am1_last_close = 0.0
    am2_last_close = 0.0
    am1_last_open = 0.0
    am2_last_open = 0.0

    parameters = []
    variables = ["f15min_open", "f15min_high", "f15min_low", "f15min_close", "f5min_open", "f5min_high", "f5min_low", "f5min_close",
                 "am1_last_close", "am2_last_close", "am1_last_open", "am2_last_open"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)


        self.bg1 = BarGenerator(self.on_bar, window=15, on_window_bar=self.on_freq1_bar)
        self.bg2 = BarGenerator(self.on_bar, window=5, on_window_bar=self.on_freq2_bar)

        self.am1 = ArrayManager(size=100)
        self.am2 = ArrayManager(size=300)


    def on_freq1_bar(self, bar: BarData):
        self.am1.update_bar(bar)
        self.write_log("15min bar: {}".format(bar.datetime))
        self.put_event()

    def on_freq2_bar(self, bar: BarData):
        self.am2.update_bar(bar)
        self.write_log("5min bar: {}".format(bar.datetime))
        self.put_event()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(4500)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg1.update_tick(tick)
        self.bg2.update_tick(tick)
        self.bg1.update_bar(self.bg1.bar)
        self.bg2.update_bar(self.bg2.bar)

        self.f15min_open = self.bg1.bar.open_price
        self.f15min_high = self.bg1.bar.high_price
        self.f15min_low = self.bg1.bar.low_price
        self.f15min_close = self.bg1.bar.close_price

        self.f5min_open = self.bg2.bar.open_price
        self.f5min_high = self.bg2.bar.high_price
        self.f5min_low = self.bg2.bar.low_price
        self.f5min_close = self.bg2.bar.close_price

        self.am1_last_close = self.am1.close_array[-1]
        self.am2_last_close = self.am2.close_array[-1]
        self.am1_last_open = self.am1.open_array[-1]
        self.am2_last_open = self.am2.open_array[-1]

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass