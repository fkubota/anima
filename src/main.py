import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg
from widget_main import MainWindow
from widget_region_pair import WidgetRegionPair


class ISedPyqt5(MainWindow):
    def __init__(self, parent=None):
        super(ISedPyqt5, self).__init__(parent)

        self.x_sec = 0
        self.segment_length_sec = 1
        self.recommend_regions = []

        # region
        self.target_region_l = 0
        self.target_region_r = 2
        # self.target_region0 = pg.LinearRegionItem(
        #                         brush='AA000044', pen='AA000044')
        # self.target_region1 = pg.LinearRegionItem(
        #                         brush='AA000044', pen='AA000044')
        self.target_region_pair = WidgetRegionPair(
                                brush='AA000044', pen='AA000044')

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

    def update_target_region(self):
        print('\n--- update_target_region')
        region = self.sender()
        left, right = region.getRegion()
        self.target_region_l = left
        self.target_region_r = right

    def first_recommend(self):
        print('\n--- first_recommend')
        recommend_sec_list = self.get_recommend_sec()
        half_region = self.segment_length_sec/2

        # recommend
        for i, rcmd_sec in enumerate(recommend_sec_list):
            region = WidgetRegionPair(brush='AAAAAA40', pen='00000077')
            region.set_id(i)
            region.region0.setRegion(
                            [rcmd_sec-half_region, rcmd_sec+half_region])
            region.region1.setRegion(
                            [rcmd_sec-half_region, rcmd_sec+half_region])
            self.w_signal.p_pg0.addItem(region.region0)
            self.w_signal.p_pg1.addItem(region.region1)
            self.recommend_regions.append(region)

        # recommend button を押せなくする
        self.btn_recommend.setEnabled(False)

        # # 最初のターゲット領域を固定
        self.target_region_pair.region0.setMovable(False)
        self.target_region_pair.region1.setMovable(False)

    def get_recommend_sec(self):
        print('\n--- get_recommend_regions')
        seg_feats = self.get_segment_feats()
        target_feat = self.get_target_feat()
        seg_scores = self.calc_scores(target_feat, seg_feats)

        # calc recommend sec
        signal = self.signal
        sr = self.sr
        segment_length_sec = self.segment_length_sec
        n_seg = int(len(signal)/sr//segment_length_sec)
        x_seg_sec = np.arange(segment_length_sec/2, n_seg, segment_length_sec)
        idxs_recommend = np.argsort(seg_scores)[:5]
        recommend_sec = x_seg_sec[idxs_recommend]
        return recommend_sec

    def get_target_feat(self):
        print('\n--- get_target_feats')
        left = self.target_region_l
        right = self.target_region_r
        signal = self.signal
        sr = self.sr
        self.x_sec = np.arange(0, len(signal))/sr
        target_idxs = (left < self.x_sec) & (self.x_sec < right)
        signal_target = signal[target_idxs]

        target_feat = self.feature_extraction(signal_target)
        target_feat = np.mean(target_feat, axis=0)
        return target_feat

    def get_segment_feats(self):
        '''
        segmentごとに特徴量を計算して、各segmentに1つの特徴量ベクトルを得る
        '''
        print('\n--- get_segment_feats')
        signal = self.signal
        sr = self.sr
        segment_length_sec = self.segment_length_sec
        n_seg = int(len(signal)/sr//segment_length_sec)
        feat_list = []
        for i_seg in range(0, n_seg):
            start_idx = int(sr*i_seg)
            end_idx = int(sr*(i_seg+segment_length_sec))
            signal_seg = signal[start_idx:end_idx]
            feats = self.feature_extraction(signal_seg)
            feat_list.append(np.mean(feats, axis=0))
        return np.array(feat_list)

    def feature_extraction(self, signal):
        feats = librosa.feature.mfcc(
                    signal,
                    sr=self.sr,
                    n_fft=2048,
                    hop_length=1024,
                    n_mels=12)
        return feats.T

    def calc_scores(self, target_feat, seg_feats):
        n_seg = seg_feats.shape[0]
        scores = []
        print(f'n_seg: {n_seg}')
        for idx in range(n_seg):
            # d(s, s_n) 対象セグメントとネガティブセグメント(ターゲット音以外)の最近傍距離
            dists = np.linalg.norm(seg_feats - seg_feats[idx], axis=1)
            min_dist_idx = np.argsort(dists)[1]
            d_nega = dists[min_dist_idx]

            # d(s, s_p) 対象セグメントとポジティブセグメント(ターゲット)の最近傍距離
            # (今は1個なので、最近傍もクソもない)
            d_posi = np.linalg.norm(seg_feats[idx] - target_feat)

            # score
            score = d_nega/(d_nega + d_posi)
            scores.append(score)
        scores = np.array(scores)
        return scores

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
            color_brush = 'AA000044' if class_ == 'Positive' else '0000AA44'
            color_pen = 'AA0000AA' if class_ == 'Positive' else '0000AAAA'
            left, right = region.getRegion()
            fix_region = pg.LinearRegionItem(brush=color_brush, pen=color_pen)
            fix_region.setRegion([left, right])
            fix_region.setMovable(False)
            self.w_signal.p_pg0.addItem(fix_region)
            self.w_signal.p_pg1.addItem(fix_region)

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
