import sys
import pandas as pd
import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler
import PyQt5.QtWidgets as QW
from widget_pbar import WidgetProgressBar


class DFHandler:
    def __init__(self, signal, sr):
        self.df_seg = pd.DataFrame()
        self.df_rel = pd.DataFrame()
        self.signal = signal
        self.sr = sr
        self.seg_length_sec = 0
        self.scaler = StandardScaler()
        self.w_pbar = WidgetProgressBar()
        self.feat_names = [
                'mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4', 'mfcc_5', 'mfcc_6',
                'mfcc_7', 'mfcc_8', 'mfcc_9', 'mfcc_10', 'mfcc_11', 'mfcc_12',
                'centroid', 'band_width', 'rolloff', 'zcr'
                ]

    def init_df_seg(self, start_sec, end_sec):
        '''
        signal, sr, start_sec, end_sec を用いてdf_segの初期化を行なう。
        特徴量抽出も行なう。
        '''
        self.seg_length_sec = end_sec - start_sec
        self.n_seg = int(round(
                            len(self.signal)/self.sr/self.seg_length_sec, 0))

        # segment 配列を定置
        seg_starts_sec = []
        for i in range(self.n_seg):
            seg_start = i * self.seg_length_sec
            seg_starts_sec.append(seg_start)
        seg_starts_sec = np.array(seg_starts_sec)

        # df_segを定義
        # columnsに、'seg_start_sec', 'label', 特徴量を持つ
        # 特徴量は、すべてNaNにしている
        self.df_seg = pd.DataFrame(seg_starts_sec, columns=['seg_start_sec'])
        self.df_seg['label'] = 'None'

        # 特徴量を作成
        self.w_pbar.lbl.setText('特徴量を計算しています')
        self.w_pbar.pbar.setMaximum(self.n_seg)
        self.w_pbar.show()
        df_feats = pd.DataFrame(columns=self.feat_names)
        for i in range(self.n_seg):
            QW.QApplication.processEvents()
            seg_start_sec = self.df_seg['seg_start_sec'].values[i]
            seg_end_sec = seg_start_sec + self.seg_length_sec

            # feats
            time = np.arange(0, len(self.signal))/self.sr
            idxs = (seg_start_sec <= time) & (time < seg_end_sec)
            feats = self.feature_extraction(self.signal[idxs])
            _df_feats = pd.DataFrame([feats], columns=self.feat_names)
            df_feats = pd.concat(
                        [df_feats, _df_feats], axis=0).reset_index(drop=True)

            # progress
            self.w_pbar.pbar.setValue(i)
        self.w_pbar.close()

        # self.scaler.fit(df_feats)
        feats = self.scaler.fit_transform(df_feats)
        df_feats = pd.DataFrame(feats, columns=self.feat_names)
        self.df_seg = pd.concat([self.df_seg, df_feats], axis=1)

    def update_df_seg(self, start_sec, end_sec, label):
        '''
        labelが振られた領域を考慮してセグメントを再定義する。
        また、領域の前後のセグメントの特徴量も再計算しないといけないことに注意
        '''
        # from pudb import set_trace; set_trace()
        print('--- update_df_seg')
        print(f'in {start_sec} - {end_sec}')
        print(self.df_seg.head())
        label_other = 'None'

        # 領域に入ってるセグメントのseg_start_segを削除
        seg_starts_sec = self.df_seg['seg_start_sec'].values
        idxs = (start_sec <= seg_starts_sec) & (seg_starts_sec < end_sec)
        self.df_seg = self.df_seg[np.logical_not(idxs)]

        # 新しいラベル付きセグメントを付与
        if end_sec in self.df_seg['seg_start_sec'].values:
            _df = pd.DataFrame({
                    'seg_start_sec': [start_sec],
                    'label': [label]
                    })
        else:
            _df = pd.DataFrame({
                    'seg_start_sec': [start_sec, end_sec],
                    'label': [label, label_other]
                    })
        self.df_seg = pd.concat(
                [self.df_seg, _df], axis=0).sort_values('seg_start_sec')
        self.df_seg = self.df_seg.reset_index(drop=True)

        # 領域前後の特徴量がNaNになるようにする
        # ただし、前後が、None以外のラベルだとNaNにしない
        seg_starts_sec = self.df_seg['seg_start_sec'].values
        lbls = self.df_seg['label'].values

        # before
        idxs = seg_starts_sec == start_sec
        idx_before = self.df_seg[idxs].index.values[0] - 1
        if (idx_before != -1):
            if ((lbls[idx_before] != 'Negative') &
               (lbls[idx_before] != 'Positive')):
                sec_before = self.df_seg.iloc[idx_before, :]['seg_start_sec']
                self.df_seg = self.df_seg.drop(index=idx_before)
                _df = pd.DataFrame(
                    {'seg_start_sec': [sec_before],
                     'label': ['None']})
                self.df_seg = pd.concat(
                            [self.df_seg, _df]).sort_values('seg_start_sec')
                self.df_seg = self.df_seg.reset_index(drop=True)

        # after
        idxs = seg_starts_sec == end_sec
        idx_after = self.df_seg[idxs].index.values[0] + 1
        if idx_after < len(lbls):
            if ((lbls[idx_after] != 'Negative') &
               (lbls[idx_after] != 'Positive')):
                sec_after = self.df_seg.iloc[idx_after, :]['seg_start_sec']
                self.df_seg = self.df_seg.drop(index=idx_after)
                _df = pd.DataFrame(
                    {'seg_start_sec': [sec_after],
                     'label': ['None']})
                self.df_seg = pd.concat(
                            [self.df_seg, _df]).sort_values('seg_start_sec')
                self.df_seg = self.df_seg.reset_index(drop=True)

        # NaNがある部分は再計算する
        self.df_seg = self.df_seg.reset_index(drop=True)
        idxs = self.df_seg['mfcc_1'].isna().values
        starts_sec = self.df_seg[idxs]['seg_start_sec'].values
        df_feats = pd.DataFrame()
        for i, st_sec in enumerate(starts_sec):
            if st_sec == len(self.signal)/self.sr:
                continue
            # segment
            idxs = self.df_seg['seg_start_sec'].values == st_sec
            idx = self.df_seg[idxs].index.values[0]
            if len(self.df_seg) <= (idx+1):
                ed_sec = len(self.signal)/self.sr
            else:
                ed_sec = self.df_seg[
                    self.df_seg.index == (idx+1)]['seg_start_sec'].values[0]
            label = self.df_seg[
                        self.df_seg.index == idx]['label'].values[0]

            # signal
            time = np.arange(0, len(self.signal))/self.sr
            idxs = (st_sec <= time) & (time < ed_sec)
            feats = self.feature_extraction(self.signal[idxs])
            feats = self.scaler.transform([feats]).T[:, 0]
            _df_feats = pd.DataFrame([feats], columns=self.feat_names)
            _df_feats['seg_start_sec'] = [st_sec]
            _df_feats['label'] = [label]
            df_feats = pd.concat(
                        [df_feats, _df_feats], axis=0).reset_index(drop=True)

            # drop
            self.df_seg = self.df_seg.drop(index=idx)
            self.df_seg = self.df_seg.sort_values('seg_start_sec')
            self.df_seg = self.df_seg.reset_index(drop=True)

        self.df_seg = pd.concat(
                        [self.df_seg, df_feats]).sort_values('seg_start_sec')
        self.df_seg = self.df_seg.reset_index(drop=True)

    def feature_extraction(self, signal):
        n_fft = int(self.sr/10)
        hop_length = int(n_fft/2)
        mfcc = librosa.feature.mfcc(
                                y=signal,
                                sr=self.sr,
                                n_mels=12,
                                n_fft=n_fft,
                                hop_length=hop_length
                                ).T
        centroid = librosa.feature.spectral_centroid(
                                y=signal,
                                sr=self.sr,
                                n_fft=n_fft,
                                hop_length=hop_length,
                                ).T
        band_width = librosa.feature.spectral_bandwidth(
                                y=signal,
                                sr=self.sr,
                                n_fft=n_fft,
                                hop_length=hop_length,
                                ).T
        rolloff = librosa.feature.spectral_rolloff(
                                y=signal,
                                sr=self.sr,
                                n_fft=n_fft,
                                hop_length=hop_length,
                                ).T
        zcr = librosa.feature.zero_crossing_rate(
                                y=signal,
                                hop_length=hop_length,
                                ).T
        print(mfcc.shape, centroid.shape, band_width.shape, rolloff.shape, zcr.shape)
        feats = np.hstack([
                        mfcc,
                        centroid,
                        band_width,
                        rolloff,
                        zcr,
                        ])
        feats = pd.DataFrame(feats).mean(axis=0).values
        return feats

    def calc_df_rel(self):
        '''
        df_seg から、df_relを計算
        df_relのcolumns: ['seg_start_sec', 'label', 'relevance']
        '''

        # weight の計算
        w = self.calc_wegiht()

        relevances = []
        for idx in range(len(self.df_seg)):
            # 自分とその他のデータフレームに分ける
            df_me = self.df_seg.iloc[[idx], :]
            df_other = self.df_seg.drop(index=idx)
            labels = df_other['label'].values

            # labelがNone以外なら計算しない
            if df_me.label.values != 'None':
                relevances.append(0)
                continue

            # posi, nega だけ取り出す
            idxs = (labels == 'Negative') | (labels == 'Positive')
            df_other = df_other[idxs]

            # 距離を計算
            feat_me = df_me.drop(['seg_start_sec', 'label'], axis=1).values
            feat_other = df_other.drop(
                            ['seg_start_sec', 'label'], axis=1).values
            # dist = np.linalg.norm(feat_other - feat_me, axis=1)
            dist = np.sqrt((np.power(feat_other - feat_me, 2)*w).sum())

            # 距離とラベルの結合
            df_label_dist = pd.DataFrame()
            df_label_dist['label'] = df_other['label'].values
            df_label_dist['dist'] = dist

            idxs = df_label_dist['label'] == 'Positive'
            dist_posi = df_label_dist[idxs]['dist'].values
            min_idx = np.argsort(dist_posi)[0]
            min_dist_posi = dist_posi[min_idx]

            idxs = df_label_dist['label'] == 'Negative'
            if np.sum(idxs) == 0:
                pass
                min_dist_nega = 1
            else:
                dist_nega = df_label_dist[idxs]['dist'].values
                min_idx = np.argsort(dist_nega)[0]
                min_dist_nega = dist_nega[min_idx]

            rel = min_dist_nega/(min_dist_nega + min_dist_posi)
        #     seg_starts_sec.append(seg_start_sec)
            relevances.append(rel)

        self.df_rel = pd.DataFrame()
        self.df_rel['seg_start_sec'] = self.df_seg['seg_start_sec'].values
        self.df_rel['label'] = self.df_seg['label'].values
        self.df_rel['relevance'] = relevances

    def calc_wegiht(self):
        labels = self.df_seg['label'].values

        if 'Negative' not in labels:
            w = 1
            return 1
        idxs = self.df_seg['label'].values == 'Positive'
        df_p = self.df_seg[idxs].drop(['seg_start_sec', 'label'], axis=1)
        idxs = self.df_seg['label'].values == 'Negative'
        df_n = self.df_seg[idxs].drop(['seg_start_sec', 'label'], axis=1)

        posi_mean = df_p.mean(axis=0)
        posi_std = np.std(df_p, axis=0)
        nega_mean = df_n.mean(axis=0)
        nega_std = np.std(df_n, axis=0)
        w = (posi_mean - nega_mean)**2 / (posi_std ** 2 + nega_std ** 2)
        w = w.values
        return w

    def recommend_regions(self):
        self.calc_df_rel()
        # from pudb import set_trace; set_trace()
        # relevance = 0 の行を削除
        idxs = self.df_rel['relevance'].values == 0
        _df = self.df_rel[np.logical_not(idxs)]

        top5_idxs = np.argsort(_df['relevance'].values)[::-1][:5]
        recommend_regions = []
        for idx in sorted(top5_idxs):
            st_idx = idx
            st_sec = _df['seg_start_sec'].values[st_idx]

            st_idxs_rel = self.df_rel['seg_start_sec'] == st_sec
            st_idx_rel = self.df_rel[st_idxs_rel].index.values[0]
            if len(self.df_rel) == (st_idx_rel + 1):
                ed_sec = len(self.signal)/self.sr
            else:
                ed_idx_rel = st_idx_rel + 1
                ed_sec = self.df_rel['seg_start_sec'].values[ed_idx_rel]
            recommend_regions.append([st_sec, ed_sec])
        return recommend_regions


def main():
    app = QW.QApplication(sys.argv)
    print(' ========================= start =========================')
    filename = librosa.util.example_audio_file()
    signal, sr = librosa.load(filename, sr=None)

    df_handler = DFHandler(signal, sr)
    df_handler.init_df_seg(1.1, 2.4)
    print('----------------======================*************1')
    print(df_handler.df_seg.head(10))

    df_handler.update_df_seg(1.5, 2.7, 'Negative')
    print('----------------======================*************2')
    print(df_handler.df_seg.head(10))

    df_handler.update_df_seg(3.2, 4.0, 'Positive')
    print('----------------======================*************3')
    print(df_handler.df_seg.head(10))

    print('----------------======================*************4')
    print(df_handler.recommend_regions())
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
