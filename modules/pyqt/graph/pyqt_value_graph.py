import numpy as np

from logger import app_logger
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
)
from modules.items.gps import GPS_AltitudeItemConfig
from modules.pyqt.pyqt_screen_widget import ScreenWidget
from modules.settings import settings
from modules.utils.array import shift_insert


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
    DISPLAY_RANGE = settings.PERFORMANCE_GRAPH_DISPLAY_RANGE
    elements = (
        PowerItemConfig.name,
        HeartRateItemConfig.name,
        WBalNormItemConfig.name,
        LapTimeItemConfig.name,
    )

    item_config = {
        PowerItemConfig.name: {
            "plot": lambda plot_data_x1, values: pg.BarGraphItem(
                x0=plot_data_x1[:-1],
                x1=plot_data_x1[1:],
                height=np.nan_to_num(values, nan=0),
                brush=pg.mkBrush(color=(0, 255, 255)),
                pen=pg.mkPen(
                    color=(255, 255, 255), width=0.01
                ),  # transparent and thin line,
            ),
            "yrange": [30, 300],  # this will adapt automatically
        },
        HeartRateItemConfig.name: {
            "plot": lambda plot_data_x1, values: pg.PlotCurveItem(
                values, pen=pg.mkPen(color=(0, 255, 0), width=2)
            ),
            "yrange": [40, 200],
        },
        WBalNormItemConfig.name: {
            "plot": lambda plot_data_x1, values: pg.PlotCurveItem(
                values, pen=pg.mkPen(color=(255, 0, 0), width=2)
            ),
            "yrange": (0, 100),
        },
    }
    p1 = None
    p2 = None
    values = None

    @staticmethod
    def get_power_max(values):
        return 100 * (int(np.nanmax(values) / 100) + 1)

    def __init__(self, parent, config):
        self.display_items = settings.PERFORMANCE_GRAPH_DISPLAY_ITEM
        self.values = {
            k: np.full(self.DISPLAY_RANGE, np.nan) for k in self.display_items
        }

        self.plot_data_x1 = []
        for i in range(self.DISPLAY_RANGE + 1):
            self.plot_data_x1.append(i)

        super().__init__(parent, config)

    def setup_ui_extra(self):
        plot = pg.PlotWidget()
        plot.setBackground(None)
        plot.setXRange(0, self.DISPLAY_RANGE)
        plot.setMouseEnabled(x=False, y=False)

        self.p1 = plot.plotItem
        self.p1.setYRange(*self.item_config[self.display_items[0]]["yrange"])

        if len(self.display_items) == 2:
            self.p1.showAxis("right")

            self.p2 = pg.ViewBox()
            self.p1.scene().addItem(self.p2)
            self.p1.getAxis("right").linkToView(self.p2)
            self.p2.setXLink(self.p1)

            self.p2.setYRange(*self.item_config[self.display_items[1]]["yrange"])
            # p2 on p1
            self.p1.setZValue(-100)
        elif len(self.display_items) > 2:
            raise ValueError("More than two graphs is not supported")

        self.layout.addWidget(plot, self.plot_y, self.plot_x, -1, -1)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    def update_y_range(self, y_range, values, plot):
        power_max = self.get_power_max(values)

        if y_range[1] != power_max:
            y_range[1] = power_max
            plot.setYRange(*y_range)

    def update_value(self, graph_key, value):
        if graph_key in self.values:
            shift_insert(self.values[graph_key], value)

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()

        if len(self.display_items) == 2:
            item_1, item_2 = self.display_items
        else:
            item_1 = self.display_items[0]
            item_2 = None

        config_1 = self.item_config[item_1]
        values_1 = self.values[item_1]

        config_2 = self.item_config[item_2] if item_2 else None
        values_2 = self.values[item_2] if item_2 else []

        if np.isfinite(values_1).any():
            self.p1.clear()

            # change max for power
            if item_1 == PowerItemConfig.name:
                self.update_y_range(config_1["yrange"], values_1, self.p1)

            self.p1.addItem(config_1["plot"](self.plot_data_x1, values_1))

        if np.isfinite(values_2).any():
            self.p2.clear()

            # change max for power
            if item_2 == PowerItemConfig.name:
                self.update_y_range(config_2["yrange"], values_2, self.p2)

            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

            self.p2.addItem(config_2["plot"](self.plot_data_x1, values_2))


class AccelerationGraphWidget(GraphWidget):
    DISPLAY_RANGE = settings.ACC_GRAPH_DISPLAY_RANGE
    DRAW_INTERVAL = settings.REALTIME_GRAPH_INTERVAL
    Y_RANGE = 0.3

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

    def __init__(self, parent, config):
        self.values = np.full((3, self.DISPLAY_RANGE), np.nan)
        super().__init__(parent, config)

    def setup_ui_extra(self):
        plot = pg.PlotWidget()
        plot.setBackground(None)
        self.p1 = plot.plotItem
        self.p1.showGrid(y=True)

        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.p3 = pg.ViewBox()
        self.p1.scene().addItem(self.p3)
        self.p3.setXLink(self.p1)

        plot.setXRange(0, self.DISPLAY_RANGE)
        plot.setMouseEnabled(x=False, y=False)

        self.layout.addWidget(plot, 1, 0, 2, 4)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    def update_value(self, value):
        shift_insert(self.values, value)

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()

        X = 0
        Y = 1
        Z = 2

        m = [x for x in self.values[X] if not np.isnan(x)]
        median = None
        if len(m):
            median = m[-1]

        if np.isfinite(self.values[X]).any():
            self.p1.clear()
            if median is not None:
                self.p1.setYRange(-self.Y_RANGE, self.Y_RANGE)

            self.p1.addItem(
                pg.PlotCurveItem(self.values[X], pen=self.pen1, connect="finite")
            )

        if np.isfinite(self.values[Y]).any():
            self.p2.clear()

            if median is not None:
                self.p2.setYRange(-self.Y_RANGE, self.Y_RANGE)

            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
            p = pg.PlotCurveItem(self.values[Y], pen=self.pen2, connect="finite")
            self.p2.addItem(p)

        if np.isfinite(self.values[Z]).any():
            self.p3.clear()

            if median is not None:
                self.p3.setYRange(-self.Y_RANGE, self.Y_RANGE)

            self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
            p = pg.PlotCurveItem(self.values[Z], pen=self.pen3, connect="finite")
            self.p3.addItem(p)


class AltitudeGraphWidget(GraphWidget):
    DISPLAY_RANGE = settings.ALTITUDE_GRAPH_DISPLAY_RANGE

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
        self.values = {
            k: np.full(self.DISPLAY_RANGE, np.nan)
            for k in [I2C_AltitudeItemConfig.name, GPS_AltitudeItemConfig.name]
        }

        self.plot_data_x1 = []
        for i in range(self.DISPLAY_RANGE):
            self.plot_data_x1.append(i)

        super().__init__(parent, config)

    def setup_ui_extra(self):
        plot = pg.PlotWidget()
        plot.setBackground(None)
        self.p1 = plot.plotItem
        self.p1.showGrid(y=True)

        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)

        plot.setXRange(0, self.DISPLAY_RANGE)
        plot.setMouseEnabled(x=False, y=False)

        self.y_range = 15
        self.y_shift = 0  # self.y_ra  nge * 0.25

        self.layout.addWidget(plot, 1, 0, 2, 4)

    def set_font_size(self, length):
        self.font_size = int(length / 7)
        self.set_minimum_size()

    def update_value(self, graph_key, value):
        if graph_key in self.values:
            shift_insert(self.values[graph_key], value)

    @qasync.asyncSlot()
    async def update_display(self):
        super().update_display()

        m = [x for x in self.values[I2C_AltitudeItemConfig.name] if not np.isnan(x)]
        median = None
        if len(m):
            median = m[-1]

        if np.isfinite(self.values[I2C_AltitudeItemConfig.name]).any():
            self.y_range = max(
                abs(min(self.values[I2C_AltitudeItemConfig.name]) - median),
                abs(max(self.values[I2C_AltitudeItemConfig.name]) - median),
            )

            if np.isnan(self.y_range) or self.y_range < 15:
                self.y_range = 15
            else:
                self.y_range = 10 * (int(self.y_range / 10) + 1)

            self.p1.clear()
            if median is not None:
                self.p1.setYRange(median - self.y_range, median + self.y_range)

            self.p1.addItem(
                pg.PlotCurveItem(
                    self.values[I2C_AltitudeItemConfig.name],
                    pen=self.pen1,
                    connect="finite",
                )
            )

        if np.isfinite(self.values[GPS_AltitudeItemConfig.name]).any():
            self.p2.clear()

            if median is not None:
                self.p2.setYRange(
                    median - self.y_range + self.y_shift,
                    median + self.y_range + self.y_shift,
                )

            self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
            p = pg.PlotCurveItem(
                self.value[GPS_AltitudeItemConfig.name], pen=self.pen2, connect="finite"
            )
            self.p2.addItem(p)
