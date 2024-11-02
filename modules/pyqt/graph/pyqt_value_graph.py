import numpy as np

from modules._pyqt import pg, qasync
from modules.items.i2c import (
    I2C_AccXItemConfig,
    I2C_AccZItemConfig,
    I2C_AccYItemConfig,
    I2C_AltitudeItemConfig,
    I2C_MStatItemConfig,
)
from modules.items.general import (
    GradeItemConfig,
    GradeSpdItemConfig,
    PowerItemConfig,
    HeartRateItemConfig,
    LapTimeItemConfig,
    WBalNormItemConfig,
    WBalItemConfig,
)
from modules.items.gps import GPS_AltitudeItemConfig
from modules.pyqt.pyqt_screen_widget import ScreenWidget
from modules.settings import settings


class GraphWidget(ScreenWidget):
    def __init__(self, parent, config):
        self.item_layout = {}

        cols = 2 if config.display.vertical else 4

        for i, e in enumerate(self.elements):
            self.item_layout[e] = (i // cols, i % cols)

        max_height = len(self.elements) // cols

        # self.item_layout[self.__class__.__name__] = (max_height, 0, -1, -1)
        self.plot_x = 0
        self.plot_y = max_height

        ScreenWidget.__init__(self, parent, config, self.item_layout)


class PerformanceGraphWidget(GraphWidget):
    elements = (
        PowerItemConfig.name,
        HeartRateItemConfig.name,
        WBalNormItemConfig.name,
        LapTimeItemConfig.name,
    )
    element_config = {
        PowerItemConfig.name: {
            "graph_key": "power_graph",
            "yrange": [30, 300],  # this will adapt automatically
        },
        HeartRateItemConfig.name: {
            "graph_key": "hr_graph",
            "yrange": [40, 200],
        },
        WBalItemConfig.name: {
            "graph_key": "w_bal_graph",
            "yrange": (0, 100),
        },
    }

    # for Power
    # brush = pg.mkBrush(color=(0,160,255,64))
    brush = pg.mkBrush(color=(0, 255, 255))
    # pen2 = pg.mkPen(color=(255,255,255,0), width=0.01) #transparent and thin line
    pen1 = pg.mkPen(color=(255, 255, 255), width=0.01)  # transparent and thin line
    # for HR, wbal
    pen2 = pg.mkPen(color=(255, 0, 0), width=2)

    def __init__(self, parent, config):
        self.display_item = settings.PERFORMANCE_GRAPH_DISPLAY_ITEM

        self.plot_data_x1 = []

        for i in range(settings.PERFORMANCE_GRAPH_DISPLAY_RANGE + 1):
            self.plot_data_x1.append(i)

        super().__init__(parent, config)

    def setup_ui_extra(self):
        # 1st graph: POWER
        plot = pg.PlotWidget()
        plot.setBackground(None)
        self.p1 = plot.plotItem

        # 2nd graph: HR or W_BAL
        self.p2 = pg.ViewBox()
        self.p1.showAxis("right")
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis("right").linkToView(self.p2)
        self.p2.setXLink(self.p1)

        plot.setXRange(0, settings.PERFORMANCE_GRAPH_DISPLAY_RANGE)
        self.p1.setYRange(*self.element_config[self.display_item[0]]["yrange"])
        self.p2.setYRange(*self.element_config[self.display_item[1]]["yrange"])
        plot.setMouseEnabled(x=False, y=False)

        # p2 on p1
        self.p1.setZValue(-100)

        self.layout.addWidget(plot, self.plot_y, self.plot_x, -1, -1)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()
        first_item, second_item = self.display_item
        first_item_config = self.element_config[first_item]
        second_item_config = self.element_config[second_item]

        # all_nan = {'hr_graph': True, 'power_graph': True}
        all_nan = {
            first_item_config["graph_key"]: True,
            second_item_config["graph_key"]: True,
        }

        for key in all_nan.keys():
            chk = np.isnan(self.sensor.values["integrated"][key])

            if False in chk:
                all_nan[key] = False

        if not all_nan[first_item_config["graph_key"]]:
            self.p1.clear()

            # change max for power
            if first_item == PowerItemConfig.name:
                power_max = 100 * (
                    int(
                        np.nanmax(
                            self.sensor.values["integrated"][
                                first_item_config["graph_key"]
                            ]
                        )
                        / 100
                    )
                    + 1
                )
                if first_item_config["yrange"][1] != power_max:
                    first_item_config["yrange"][1] = power_max
                    self.p1.setYRange(*first_item_config["yrange"])

            self.p1.addItem(
                pg.BarGraphItem(
                    x0=self.plot_data_x1[:-1],
                    x1=self.plot_data_x1[1:],
                    height=self.sensor.values["integrated"][
                        first_item_config["graph_key"]
                    ],
                    brush=self.brush,
                    pen=self.pen1,
                )
            )

        # if not all_nan['hr_graph']:
        if not all_nan[second_item_config["graph_key"]]:
            self.p2.clear()
            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
            # for HR
            self.p2.addItem(
                pg.PlotCurveItem(
                    self.sensor.values["integrated"][second_item_config["graph_key"]],
                    pen=self.pen2,
                )
            )


class AccelerationGraphWidget(GraphWidget):
    elements = (
        I2C_AccXItemConfig.name,
        I2C_AccYItemConfig.name,
        I2C_AccZItemConfig.name,
        I2C_MStatItemConfig.name,
    )

    # for acc
    pen1 = pg.mkPen(color=(0, 0, 255), width=3)
    pen2 = pg.mkPen(color=(255, 0, 0), width=3)
    pen3 = pg.mkPen(color=(0, 0, 0), width=2)

    g_range = 0.3

    def setup_ui_extra(self):
        plot = pg.PlotWidget()
        plot.setBackground(None)
        self.p1 = plot.plotItem
        self.p1.showGrid(y=True)
        # self.p1.setLabels(left='HR')

        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.p3 = pg.ViewBox()
        self.p1.scene().addItem(self.p3)
        self.p3.setXLink(self.p1)

        plot.setXRange(0, settings.ACC_TIME_RANGE)
        plot.setMouseEnabled(x=False, y=False)

        self.layout.addWidget(plot, 1, 0, 2, 4)

    def start(self):
        self.timer.start(settings.REALTIME_GRAPH_INTERVAL)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()

        X = 0
        Y = 1
        Z = 2

        v = self.sensor.sensor_i2c.graph_values["g_acc"]
        all_nan = {X: True, Y: True, Z: True}
        for key in all_nan.keys():
            chk = np.isnan(v[key])
            if False in chk:
                all_nan[key] = False
        m = [x for x in v[0] if not np.isnan(x)]
        median = None
        if len(m):
            median = m[-1]

        if not all_nan[X]:
            self.p1.clear()
            if median is not None:
                self.p1.setYRange(-self.g_range, self.g_range)

            self.p1.addItem(pg.PlotCurveItem(v[X], pen=self.pen1, connect="finite"))

        if not all_nan[Y]:
            self.p2.clear()

            if median is not None:
                self.p2.setYRange(-self.g_range, self.g_range)

            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
            p = pg.PlotCurveItem(v[Y], pen=self.pen2, connect="finite")
            self.p2.addItem(p)

        if not all_nan[Z]:
            self.p3.clear()

            if median is not None:
                self.p3.setYRange(-self.g_range, self.g_range)

            self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
            p = pg.PlotCurveItem(v[Z], pen=self.pen3, connect="finite")
            self.p3.addItem(p)


class AltitudeGraphWidget(GraphWidget):
    elements = (
        GradeItemConfig.name,
        GradeSpdItemConfig.name,
        I2C_AltitudeItemConfig.name,
        GPS_AltitudeItemConfig.name,
    )

    # for altitude_raw
    pen1 = pg.mkPen(color=(0, 0, 0), width=2)
    pen2 = pg.mkPen(color=(255, 0, 0), width=3)

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.plot_data_x1 = []
        for i in range(settings.PERFORMANCE_GRAPH_DISPLAY_RANGE):
            self.plot_data_x1.append(i)

    def setup_ui_extra(self):
        plot = pg.PlotWidget()
        plot.setBackground(None)
        self.p1 = plot.plotItem
        self.p1.showGrid(y=True)

        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)

        plot.setXRange(0, settings.PERFORMANCE_GRAPH_DISPLAY_RANGE)
        plot.setMouseEnabled(x=False, y=False)

        self.y_range = 15
        self.y_shift = 0  # self.y_ra  nge * 0.25

        self.layout.addWidget(plot, 1, 0, 2, 4)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()

        v = self.sensor.values["integrated"]
        all_nan = {"altitude_graph": True, "altitude_gps_graph": True}
        for key in all_nan.keys():
            chk = np.isnan(v[key])
            if False in chk:
                all_nan[key] = False
        m = [x for x in v["altitude_graph"] if not np.isnan(x)]
        median = None
        if len(m):
            median = m[-1]

        if not all_nan["altitude_graph"]:
            self.y_range = max(
                abs(min(v["altitude_graph"]) - median),
                abs(max(v["altitude_graph"]) - median),
            )

            if np.isnan(self.y_range) or self.y_range < 15:
                self.y_range = 15
            else:
                self.y_range = 10 * (int(self.y_range / 10) + 1)

            self.p1.clear()
            if median is not None:
                self.p1.setYRange(median - self.y_range, median + self.y_range)

            self.p1.addItem(
                pg.PlotCurveItem(v["altitude_graph"], pen=self.pen1, connect="finite")
            )

        if not all_nan["altitude_gps_graph"]:
            self.p2.clear()

            if median is not None:
                self.p2.setYRange(
                    median - self.y_range + self.y_shift,
                    median + self.y_range + self.y_shift,
                )

            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
            p = pg.PlotCurveItem(
                v["altitude_gps_graph"], pen=self.pen2, connect="finite"
            )
            self.p2.addItem(p)
