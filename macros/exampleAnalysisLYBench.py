import ROOT as R
from root_pandas import read_root

R.gROOT.SetBatch(1)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='inputData')
parser.add_argument('--inputEnvData',dest='inputEnvData')
parser.add_argument('--output',dest='output')
args = parser.parse_args()

#helper class to access environmental data
class TempData:
    #load data from ROOT file and transform in pandas DF
    def __init__(self, inputFile):
        self.df=read_root(inputFile)
        self.df.set_index('timestamp', inplace=True)

    #return the closest environmental data values to a timestamp index
    def closestValues(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]

    #return the closest bench temperature to a timestamp index
    def tBench(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]['tbench']

    #return the closest lab temperature to a timestamp index
    def tLab(self, timeStamp):
        return self.df.iloc[self.df.index.get_loc(timeStamp,method='nearest')]['tlab']


tData=TempData(args.inputEnvData)

data=R.TFile(args.inputData)
h4=data.Get("h4")

histos={}
histos['charge']=R.TH1F("charge","charge",500,0,100000);
histos['tBench']=R.TH1F("tBench","tBench",1000,15.,25.);
histos['tLab']=R.TH1F("tLab","tLab",1000,15.,25.);

for ievent,event in enumerate(h4):
    if (ievent%100==0):
        print "Analysing event %d"%ievent
        #fill environmental data histograms only every 100 events
        #get closest value of environmental data 
        t=tData.closestValues(event.time_stamps[1])
        histos['tBench'].Fill(t['tbench'])
        histos['tLab'].Fill(t['tlab'])

    histos['charge'].Fill(event.charge_tot[event.C0])

print "Average temperature during run: %4.2f"%(histos['tBench'].GetMean())

print "Saving histograms to "+args.output
fOut=R.TFile(args.output,"RECREATE")
for hn, histo in histos.iteritems():
    if isinstance(histo,R.TH1F):
        histo.SetMinimum(0.)
    if isinstance(histo,R.TGraphAsymmErrors):
        histo.SetMinimum(0.)
        histo.SetMaximum(1.1)
    histo.Write()
fOut.Close()



