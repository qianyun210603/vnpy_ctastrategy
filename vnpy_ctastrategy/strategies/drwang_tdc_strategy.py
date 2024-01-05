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
import numpy as np


class TDCCalculator:
    pass




class DrWangTDCStrategy(CtaTemplate):
    author = "Cui"

    num_continious_bars = 6
    num_confirmed_bars = 9
    back_shift = 4
    monitor_freq1 = 5
    monitor_freq2 = 15

    tdc_freq1 = -1000000
    tdc_freq2 = -1000000

    parameters = ["num_continious_bars", "num_confirmed_bars", "back_shift", "monitor_freq1", "monitor_freq2"]
    variables = ["tdc_freq1", "tdc_freq2"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        assert self.monitor_freq1 > self.monitor_freq2, "monitor_freq1 should be larger than monitor_freq2"
        assert self.monitor_freq1 % self.monitor_freq2 == 0, "monitor_freq1 should be a multiple of monitor_freq2"


        self.bg = BarGenerator(self.on_bar)
        self.bg1 = BarGenerator(self.on_bar, self.monitor_freq1, self.on_freq1_bar)
        if self.monitor_freq2 == 1:
            self.bg2 = self.bg
        else:
            self.bg2 = BarGenerator(self.on_bar, self.monitor_freq2, self.on_freq2_bar)
        _size_am2 = self.monitor_freq2//self.monitor_freq1*300
        self.ams = (ArrayManager(size=300), ArrayManager(size=_size_am2))
        self.tdc_arraies = (np.zeros(300), np.zeros(_size_am2))
        self.ns_setup_phases = (np.zeros(300), np.zeros(_size_am2))
        self.ns_num_long_countdowns = (np.ones(300)*1000, np.ones(_size_am2)*1000)
        self.ns_num_short_countdowns = (np.ones(300)*1000, np.ones(_size_am2)*1000)
        self.ns_prev_count_close = (np.zeros(300), np.zeros(_size_am2))
        self.ns_sline = (np.zeros(300), np.zeros(_size_am2))
        self.ns_bline = (np.zeros(300), np.zeros(_size_am2))



    def on_freq1_bar(self, bar: BarData):
        pass

    def on_freq2_bar(self, bar: BarData):
        pass

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(1000)

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
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
        cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

        if cross_over:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)

        elif cross_below:
            if self.pos == 0:
                self.short(bar.close_price, 1)
            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

        if self.monitor_freq2 == 1:
            self.on_freq2_bar(bar)

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