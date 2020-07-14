import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg
from widget_main import MainWindow
from widget_region_pair import WidgetRegionPair
from df_handler import DFHandler


class ISedPyqt5(MainWindow):
    def __init__(self, parent=None):
        super(ISedPyqt5, self).__init__(parent)

        self.x_sec = 0
        self.segment_length_sec = 1
        self.recommend_regions = []
        self.df_handler = None

        # region
        self.target_region_l = 1
        self.target_region_r = 2
        self.target_region_pair = WidgetRegionPair(
                                brush='0000AA44', pen='0000AA44')

        # bar
        self.bar_0 = pg.InfiniteLine(
                            pen='000000', hoverPen='FF000055', movable=True)
        self.bar_1 = pg.InfiniteLine(
                            pen='000000', hoverPen='FF000055', movable=True)

        # init method
        self.init_method()
        self.init_event()

    def init_method(self):
        self.w_mp.player.setNotifyInterval(100)
        self.w_signal.p_pg0.addItem(self.bar_0)
        self.w_signal.p_pg1.addItem(self.bar_1)

    def init_event(self):
        self.target_region_pair.region0.sigRegionChanged.connect(
                                                    self.update_target_region)
        self.target_region_pair.region1.sigRegionChanged.connect(
                                                    self.update_target_region)
        self.btn_recommend.clicked.connect(self.first_recommend)
        self.w_list.btn_find.clicked.connect(self.clicked_btn_find)
        self.w_list.btn_posi.clicked.connect(self.clicked_btn_posi_nega)
        self.w_list.btn_nega.clicked.connect(self.clicked_btn_posi_nega)
        self.btn_open.clicked.connect(self.show_first_region)
        self.w_mp.player.positionChanged.connect(self.player_position_changed)
        self.bar_0.sigPositionChanged.connect(self.update_bar_pos)
        self.bar_1.sigPositionChanged.connect(self.update_bar_pos)

    def show_first_region(self):
        self.w_signal.p_pg0.addItem(self.target_region_pair.region0)
        self.w_signal.p_pg1.addItem(self.target_region_pair.region1)
        self.df_handler = DFHandler(self.signal, self.sr)

    def update_target_region(self):
        print('\n--- update_target_region')
        region = self.sender()
        left, right = region.getRegion()
        self.target_region_l = left
        self.target_region_r = right

    def first_recommend(self):
        print('\n--- first_recommend')
        left = self.target_region_l
        right = self.target_region_r
        self.df_handler.init_df_seg(left, right)
        self.df_handler.update_df_seg(left, right, 'Positive')
        # recommend_sec_list = self.get_recommend_sec()
        # half_region = self.segment_length_sec/2
        recommend_regions = self.df_handler.recommend_regions()

        # recommend
        for i, pos in enumerate(recommend_regions):
            region = WidgetRegionPair(brush='AAAAAA40', pen='000000AA')
            region.set_id(i)
            region.region0.setRegion([pos[0], pos[1]])
            region.region1.setRegion([pos[0], pos[1]])
            self.w_signal.p_pg0.addItem(region.region0)
            self.w_signal.p_pg1.addItem(region.region1)
            self.recommend_regions.append(region)

        # recommend button を押せなくする
        self.btn_recommend.setEnabled(False)

        # # 最初のターゲット領域を固定
        self.target_region_pair.region0.setMovable(False)
        self.target_region_pair.region1.setMovable(False)

    def recommend(self):
        print('\n--- recommend')
        recommend_regions = self.df_handler.recommend_regions()
        print(recommend_regions)

        # recommend
        for i, pos in enumerate(recommend_regions):
            region = self.recommend_regions[i]
            region.region0.setRegion([pos[0], pos[1]])
            region.region1.setRegion([pos[0], pos[1]])
            self.w_signal.p_pg0.addItem(region.region0)
            self.w_signal.p_pg1.addItem(region.region1)

    def clicked_btn_find(self):
        '''
        findボタンがクリックされたら動く。
        1. レコメンドリージョン全てにクラスが割り振られているかチェック。 <--- 未実装
        2. クラスに応じて色を付けたリージョンを描画。
        3. リージョンを動かせないように固定。
        4. レコメンドリージョンのクラスを初期化(None)にする。
        5. レコメンドリストを初期化。
        6. 次のリージョンをレコメンド(レコメンドリージョンは使いまわす)。
        '''
        for i_region, region in enumerate(self.recommend_regions):
            class_ = region.class_
            color_brush = '0000AA44' if class_ == 'Positive' else 'AA000044'
            color_pen = '0000AA44' if class_ == 'Positive' else 'AA000044'
            left, right = region.region0.getRegion()
            fix_region0 = pg.LinearRegionItem(brush=color_brush, pen=color_pen)
            fix_region0.setRegion([left, right])
            fix_region0.setMovable(False)
            fix_region1 = pg.LinearRegionItem(brush=color_brush, pen=color_pen)
            fix_region1.setRegion([left, right])
            fix_region1.setMovable(False)
            self.w_signal.p_pg0.addItem(fix_region0)
            self.w_signal.p_pg1.addItem(fix_region1)

            # df_seg を update
            self.df_handler.update_df_seg(left, right, class_)

        self.recommend()

    def clicked_btn_posi_nega(self):
        '''
        Positive/Negative ボタンがクリックされたら、リージョンとリストのクラスを更新
        '''
        sender = self.sender()
        row = self.w_list.list.currentRow()
        if sender.text() == 'Positive':
            text = 'Positive'
        elif sender.text() == 'Negative':
            text = 'Negative'

        self.recommend_regions[row].set_class(text)
        btn_text = f'Region #{row} ---> {text}'
        self.w_list.list.item(row).setText(btn_text)

    def player_position_changed(self, pos, senderType=False):
        '''
        music player の時間に変更があったら動く関数
        '''
        pos_sec = pos/1000
        self.bar_0.setPos(pos_sec)
        self.bar_1.setPos(pos_sec)

    def update_bar_pos(self):
        sender = self.sender()
        pos = sender.getPos()[0]
        # bar を連動させる
        if sender == self.bar_0:
            self.bar_1.setPos(pos)
        elif sender == self.bar_1:
            self.bar_0.setPos(pos)

        # musicplayerの再生位置の調整
        self.w_mp.player.setPosition(pos*1000)  # ms 単位で渡す


def main():
    app = QW.QApplication(sys.argv)

    w = ISedPyqt5()
    w.move(300, 500)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
