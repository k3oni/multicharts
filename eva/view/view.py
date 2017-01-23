#!/usr/bin/python
################################################################################

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick
from pprint import pprint

class view:

    def __init__(self):
        self.color = dict()
        self.color['black'] = '#07000d'
        self.color['darkblue'] = '#5998ff'
        self.color['volume'] = '#00ffe8'
        self.color['colorup'] = '#9eff15'
        self.color['colordown'] = '#ff1717'
        self.XmaxNLocator = 50
        self.YmaxNLocator = 100
        self.candleRowSpanWithoutVolume = 5
        self.candleRowSpanWithVolume = 4
        self.plt = plt 

    def drawSomething(self):
        pass

    def draw(self, instru, date, open, high, low, close, volume = None, \
                    savefile = None, **kwarg):

        date = self.multiChartDate2MatPlotDate(date)
        candles = zip(*(date, open, close, high, low))
        
        # figure color
        if 'figsize' in kwarg.keys():
            fig = plt.figure(facecolor=self.color['black'], figsize=kwarg['figsize'])
        else:
            fig = plt.figure(facecolor=self.color['black'])

        # subplot for candlesticks
        rowspan = self.candleRowSpanWithoutVolume if volume == None else \
                    self.candleRowSpanWithVolume 
        ax1 = plt.subplot2grid((5,5), (0,0), rowspan=rowspan, colspan=5, \
                                axisbg=self.color['black'])
        candlestick(ax1, candles, width=1, colorup=self.color['colorup'], \
                        colordown=self.color['colordown'], alpha=0.8, shadowcolor='w')

        ## x axis
        # show white grid        
        ax1.grid(True, color='w')        
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(self.XmaxNLocator))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.tick_params(axis='x', colors='w')

        # shall rotate x tick
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        # tick on y axis is set to white
        ax1.tick_params(axis='y', colors='w')
        ax1.yaxis.label.set_color('w')
        ax1.yaxis.set_major_locator(mticker.MaxNLocator(self.YmaxNLocator))
        plt.ylabel('Price')

        # show boundary
        ax1.spines['bottom'].set_color(self.color['darkblue'])
        ax1.spines['top'].set_color(self.color['darkblue'])
        ax1.spines['left'].set_color(self.color['darkblue'])
        ax1.spines['right'].set_color(self.color['darkblue'])

        
        # subplot for volume
        if volume <> None:
            # set ax1 tick invisible
            plt.setp(ax1.get_xticklabels(), visible=False)
            # share the same axis with axis 1        
            ax2 = plt.subplot2grid((5,5),(4,0), sharex=ax1, rowspan=1, \
                                    colspan=5, axisbg=self.color['black'])
            # plot volume
            ax2.plot(date, volume, self.color['volume'], linewidth=0.8)
            ax2.fill_between(date, volume.min(), volume, \
                                facecolor=volColor, alpha=0.5)
            # grid
            ax2.grid(True, color='w')
        
            # x axis
            ax2.xaxis.set_major_locator(mticker.MaxNLocator(self.XmaxNLocator))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            for label in ax2.xaxis.get_ticklabels():
                label.set_rotation(45)
            ax2.tick_params(axis='x', colors='w')
            
            # y axis
            plt.ylabel('Volume')    
            ax2.axes.yaxis.set_ticklabels([])
            ax2.yaxis.label.set_color('w')
            ax2.tick_params(axis='y', colors='w')

            # boundary
            ax2.spines['bottom'].set_color(self.color['darkblue'])
            ax2.spines['top'].set_color(self.color['darkblue'])
            ax2.spines['left'].set_color(self.color['darkblue'])
            ax2.spines['right'].set_color(self.color['darkblue'])
            plt.subplots_adjust(left=0.09, bottom=0.14, right=0.94, top=0.95, wspace=0.2, hspace=0)        
        
        plt.suptitle('%s price' % instru, color='w')
        
        # user defined drawing
        
        self.userDraw(ax1, kwarg)
        plt.show()
        if savefile <> None:
            fig.savefig(savefile, facecolor=fig.get_facecolor(), dpi=400)


    def userDraw(self, ax, operation):
        if 'region' in operation.keys():
            args = operation['region']
            if 'colors' in operation.keys():
                colors = operation['colors']
            for regionId in args.keys():
                upper = []
                lower = []
                reg = args[regionId]
                for d in sorted(reg.keys()):
                    lower.append(reg[d][0])
                    upper.append(reg[d][1])
                self.plotRegion(ax, sorted(reg.keys()), upper, lower, color=colors[regionId])

        if 'specialDay' in operation.keys():
            spd = operation['specialDay']
            self.plotSpecialDate(ax, spd['dates'], spd['open'], spd['high'],\
                                     spd['low'], spd['close'])
            

    def plotSpecialDate(self, ax, date, open, high, low, close):
        date = self.multiChartDate2MatPlotDate(date)
        candles = zip(*(date, open, close, high, low))
        candlestick(ax, candles, width=1, colorup=self.color['colorup'], \
                        colordown=self.color['colordown'], alpha=0.8, shadowcolor='w',\
                        showboundary=True, boundaryedgecolor='b', boundarywidth=0.5)
        

    def plotRegion(self, ax, date, upper, lower, color='r'):
        date = self.multiChartDate2MatPlotDate(date)
        ax.fill_between(date, lower, upper, facecolor=color, alpha=0.8)


    def multiChartDate2MatPlotDate(self, dates):
        converter = mdates.strpdate2num('%Y%m%d')       
        def date2mdate(d):
            dstr = str(int(d))
            date = '20' + dstr[1:]
            return converter(date)
        dates = map(date2mdate, dates)
        return dates

if __name__ == "__name__":
    v = view()
    view.drawSomething() 
