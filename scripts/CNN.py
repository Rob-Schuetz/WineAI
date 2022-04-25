"""
1D CNN class to convert take daily weather conditions 
and convert them into rolling months (~180, n filters,)
"""

from tensorflow.keras.layers import Layer, Conv1D, AveragePooling1D, MaxPooling1D

class CNNBlock(Layer):
    def __init__(self, wfilt=32, mfilt=32, pool='max', act='relu'):
        super(CNNBlock, self).__init__()
        self.conv_week = Conv1D(filters=wfilt, kernel_size=7, activation=act, bias_initializer='glorot_uniform', name='WeekConv')
        self.conv_month = Conv1D(filters=mfilt, kernel_size=4, activation=act, bias_initializer='glorot_uniform', name='MonthConv')
        self.pool = pool
        self.apool_month = AveragePooling1D(pool_size=1, name='AvgMonthPool')
        self.mpool_month = MaxPooling1D(pool_size=1, name='MaxMonthPool')

    def __call__(self, inputs):
        x = self.conv_week(inputs)
        x = self.conv_month(x)
        if self.pool == 'avg':
            x = self.apool_month(x)
        elif self.pool == 'max':
            x = self.mpool_month(x)

        return x