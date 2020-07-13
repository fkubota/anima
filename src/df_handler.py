import pandas as pd
import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler


class DFHandler:
    def __init__(self, signal, sr):
        self.df_seg = pd.DataFrame()
        self.signal = signal
        self.sr = sr
        self.seg_length_sec = 0
        self.feat_names = [f'mfcc_{i+1}' for i in range(12)]
        self.scaler = StandardScaler()

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
        df_feats = pd.DataFrame(columns=self.feat_names)
        for i in range(self.n_seg):
            seg_start_sec = self.df_seg['seg_start_sec'].values[i]
            seg_end_sec = seg_start_sec + self.seg_length_sec

            # feats
            time = np.arange(0, len(self.signal))/self.sr
            idxs = (seg_start_sec <= time) & (time < seg_end_sec)
            feats = self.feature_extraction(self.signal[idxs])
            # feats = pd.DataFrame(feats.T).mean(axis=0).values
            _df_feats = pd.DataFrame([feats], columns=self.feat_names)
            df_feats = pd.concat(
                        [df_feats, _df_feats], axis=0).reset_index(drop=True)

        # self.scaler.fit(df_feats)
        feats = self.scaler.fit_transform(df_feats)
        df_feats = pd.DataFrame(feats, columns=self.feat_names)
        self.df_seg = pd.concat([self.df_seg, df_feats], axis=1)

    def update_df_seg(self, start_sec, end_sec, label):
        '''
        labelが振られた領域を考慮してセグメントを再定義する。
        また、領域の前後のセグメントの特徴量も再計算しないといけないことに注意
        '''
        _start_sec = start_sec - 10**(-2)
        label_other = 'Negative' if label == 'Positive' else 'Positive'

        # 領域に入ってるセグメントを削除
        seg_starts_sec = self.df_seg['seg_start_sec'].values
        idxs = (_start_sec <= seg_starts_sec) & (seg_starts_sec < end_sec)
        self.df_seg = self.df_seg[np.logical_not(idxs)]

        # 新しいラベル付きセグメントを付与
        _df = pd.DataFrame({
                'seg_start_sec': [start_sec, end_sec],
                'label': [label, label_other]
                })
        self.df_seg = pd.concat(
                [self.df_seg, _df], axis=0).sort_values('seg_start_sec')
        self.df_seg = self.df_seg.reset_index(drop=True)

        # 領域前後の特徴量がNaNになるようにする
        seg_starts_sec = self.df_seg['seg_start_sec'].values
        idxs = seg_starts_sec == start_sec
        idx_before = self.df_seg[idxs].index.values[0] - 1
        sec_before = self.df_seg.iloc[idx_before, :]['seg_start_sec']
        idxs = seg_starts_sec == end_sec
        idx_after = self.df_seg[idxs].index.values[0] + 1
        sec_after = self.df_seg.iloc[idx_after, :]['seg_start_sec']

        # 領域前後のセグメントを削除
        self.df_seg = self.df_seg.drop(index=[idx_before, idx_after])

        # 領域前後の要素を挿入(特徴量はNaNになる)
        _df = pd.DataFrame(
            {'seg_start_sec': [sec_before, sec_after],
             'label': ['None', 'None']})
        self.df_seg = pd.concat(
                        [self.df_seg, _df]).sort_values('seg_start_sec')
        self.df_seg = self.df_seg.reset_index(drop=True)

        # NaNがある部分は再計算する
        idxs = self.df_seg['mfcc_1'].isna().values
        starts_sec = self.df_seg[idxs]['seg_start_sec'].values
        df_feats = pd.DataFrame()
        for i, start_sec in enumerate(starts_sec):
            # segment
            idxs = self.df_seg['seg_start_sec'].values == start_sec
            idx = self.df_seg[idxs].index.values[0]
            end_sec = self.df_seg[
                        self.df_seg.index == idx+1]['seg_start_sec'].values[0]
            label = self.df_seg[
                        self.df_seg.index == idx]['label'].values[0]

            # signal
            time = np.arange(0, len(self.signal))/self.sr
            _start_sec = start_sec - 10**(-2)
            idxs = (start_sec <= time) & (time < end_sec)
            feats = self.feature_extraction(self.signal[idxs])
            feats = self.scaler.transform([feats]).T[:, 0]
            _df_feats = pd.DataFrame([feats], columns=self.feat_names)
            _df_feats['seg_start_sec'] = start_sec
            _df_feats['label'] = label
            df_feats = pd.concat(
                        [df_feats, _df_feats], axis=0).reset_index(drop=True)

            # drop
            self.df_seg = self.df_seg.drop(index=idx)
        self.df_seg = pd.concat(
                        [self.df_seg, df_feats]).sort_values('seg_start_sec')

    def feature_extraction(self, signal):
        n_fft = int(self.sr/10)
        hop_length = int(n_fft/2)
        feats = librosa.feature.mfcc(
                                y=signal,
                                sr=self.sr,
                                n_mels=12,
                                n_fft=n_fft,
                                hop_length=hop_length)
        feats = pd.DataFrame(feats.T).mean(axis=0).values
        return feats


def main():
    print(' ========================= start =========================')
    filename = librosa.util.example_audio_file()
    signal, sr = librosa.load(filename, sr=None)

    df_handler = DFHandler(signal, sr)
    df_handler.init_df_seg(1.1, 2.4)
    print('----------------======================*************1')
    print(df_handler.df_seg.head(10))

    df_handler.update_df_seg(1.1, 2.7, 'Negative')
    print('----------------======================*************2')
    print(df_handler.df_seg.head(10))

    df_handler.update_df_seg(5.2, 6.0, 'Positive')
    print('----------------======================*************2')
    print(df_handler.df_seg.head(10))



if __name__ == '__main__':
    main()
