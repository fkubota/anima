import sys
import numpy as np
import librosa
import PyQt5.QtWidgets as QW
import pyqtgraph as pg
from widget_main import MainWindow


class ISedPyqt5(MainWindow):
    def __init__(self, parent=None):
        super(ISedPyqt5, self).__init__(parent)

        self.x_sec = 0
        self.segment_length_sec = 1

        # region
        self.target_region_l = 0
        self.target_region_r = 2
        self.target_region = pg.LinearRegionItem(brush='DAFF3720')

        # event
        self.target_region.sigRegionChanged.connect(self.update_target_region)
        self.btn_recommend.clicked.connect(self.recommend)

        # init method
        self.init_gui()

    def init_gui(self):
        self.w_signal.p_pg_signal.addItem(self.target_region)

    def update_target_region(self):
        print('\n--- update_target_region')
        region = self.sender()
        left, right = region.getRegion()
        self.target_region_l = left
        self.target_region_r = right

    def recommend(self):
        print('\n--- recommend')
        recommend_sec_list = self.get_recommend_sec()
        half_region = self.segment_length_sec/2

        for rcmd_sec in recommend_sec_list:
            a = pg.LinearRegionItem(brush='AAAAAA20')
            a.setRegion([rcmd_sec-half_region, rcmd_sec+half_region])
            self.w_signal.p_pg_signal.addItem(a)

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


def main():
    app = QW.QApplication(sys.argv)

    w = ISedPyqt5()
    filename = librosa.util.example_audio_file()
    w.le_wav_path.setText(filename)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
