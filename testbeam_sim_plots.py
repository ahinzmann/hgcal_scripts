print("import")

from ROOT import TChain, gROOT, gStyle, TH1F, TCanvas, TLegend
import ROOT
import array, math
#import numpy as np
import os
from math import *
from DataFormats.FWLite import Events, Handle
import pickle

print("start")

#! /usr/bin/env python         

if __name__=="__main__":

 pointsX=array.array("f",[])
 pointsXErr=array.array("f",[])
 pointsYresponse=array.array("f",[])
 pointsYresponseErr=array.array("f",[])
 pointsYresolution=array.array("f",[])
 pointsYresolutionErr=array.array("f",[])
 
 def layer(id):
   kHGCalLayerOffset = 17
   kHGCalLayerMask = 0x1F
   return ((int(id) >> kHGCalLayerOffset) & kHGCalLayerMask) - 7 # remove 7 silicon-only layers
 
 particle="Electron"
 #particle="Muon"
 #particle="delay0" #noDigi, delay13, delay15, localTime
 stackname="_cernstack"

 simulation_output={}
 #for particleEnergy in ([1,1.6,2,3,4,5,5.6] if particle=="Electron" else [5]): #[2,3,4,5,6,7,8,9,10] # DESY stack
 for particleEnergy in ([20] if particle=="Electron" else [5]): #[2,3,4,5,6,7,8,9,10] # CERN stack
  
  version=str(particleEnergy)+"GeV"+particle

  print("start ROOT")
  gROOT.Reset()
  gROOT.SetStyle("Plain")
  gROOT.SetBatch()
  gStyle.SetOptStat(0)
  gStyle.SetOptFit(0)
  gStyle.SetTitleOffset(1.2,"Y")
  gStyle.SetPadLeftMargin(0.16)
  gStyle.SetPadBottomMargin(0.16)
  gStyle.SetPadTopMargin(0.05)
  gStyle.SetPadRightMargin(0.05)
  gStyle.SetMarkerSize(2.5)
  gStyle.SetHistLineWidth(1)
  gStyle.SetStatFontSize(0.020)
  gStyle.SetTitleSize(0.06, "XYZ")
  gStyle.SetLabelSize(0.05, "XYZ")
  gStyle.SetNdivisions(505, "XYZ")
  gStyle.SetLegendBorderSize(0)
  gStyle.SetPadTickX(1)
  gStyle.SetPadTickY(1)
  gStyle.SetEndErrorSize(5)

  #print "start CMS_lumi"

  #gROOT.LoadMacro("CMS_lumi.C");
  #iPeriod = 4;       #// 1=7TeV, 2=8TeV, 3=7+8TeV, 7=7+8+13TeV 
  #iPos = 11;
  #layers=8 # DESY stack
  layers=15 # CERN stack
  x_offset=1 #cm
  y_offset=160 #cm
  z_offset=406.581 #cm (zHGCal6=zHGCalHEmix1)
  z_max=8*4.2 #cm

  histograms=[
  #("n_SimHits",0,1000,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","size","Number of SimHits","Events"),
  #("SimHit_n_vs_layer",0.5,layers+0.5,layers,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Layer number","SimHits per layer"),
  #("SimHit_energy",0,0.005,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","SimHit energy [GeV]","Hits per event"),
  #("SimHit_energy_vs_layer",0.5,layers+0.5,layers,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Layer number","SimHit energy per layer [GeV]"),
  #("n_DigisNano",0,100,100,"nanoaodFlatTable_hgcDigiHEbackTable__GENSIMDIGIRECO","size","Number of Digis","Events"),
  #("DigiNano_data",0,500,100,"nanoaodFlatTable_hgcDigiHEbackTable__GENSIMDIGIRECO","data","ADC counts","Hits per event"),
  #("n_Digis",0,100,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","size","Number of Digis","Events"),
  ("Digi_n_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","Number of Digis per layer"),
  ("Digi_n_integral",-0.5,300.5,301,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Number of Digis per event","Fraction of events"),
  #("Digi_data",0,500,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC counts","Hits per event"),
  ("Digi_data_integral",0,10000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per event","Fraction of events"),
  ("Digi_data_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","ADC counts per layer"),
  #("Digi_dataoutoftime",0,500,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Out-of-time ADC counts","Hits per event"),
  #("Digi_dataoutoftime_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","Out-of-time ADC counts per layer"),
  #("n_UncalibratedRecHits",0,100,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","size","Number of uncalibrated RecHits","Events"),
  #("UncalibratedRecHits_n_vs_layer",0.5,layers+0.5,layers,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Layer number","Number of RecHits per layer"),
  #("UncalibratedRecHits_amplitude",0,100,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of MIPs","Hits per event"),
  #("UncalibratedRecHits_amplitude_vs_layer",0.5,layers+0.5,layers,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Layer number","Number of MIPs per layer"),
  #("n_RecHits",0,100,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","size","Number of calibrated RecHits","Events"),
  #("RecHits_n_vs_layer",0.5,layers+0.5,layers,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Layer number","Number of RecHits per layer"),
  #("RecHits_energy",0,5,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Calibrated RecHit Energy [GeV]","Hits per event"),
  #("RecHits_energy_vs_layer",0.5,layers+0.5,layers,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Layer number","Energy sum per layer [GeV]"),
  #("n_LayerClusters",0,100,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","size","Number of LayerClusters","Events"),
  #("LayerCluster_energy",0,5,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","energy","LayerCluster Energy [GeV]","Clusters per event"),
  #("LayerCluster_x",-100,100,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","x","LayerCluster x [cm]","Clusters per event"),
  #("LayerCluster_y",-100,100,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","y","LayerCluster y [cm]","Clusters per event"),
  #("LayerCluster_z",0,z_max,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","z","LayerCluster z [cm]","Clusters per event"),
  #("LayerCluster_energy_vs_z",0,z_max,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","energy","LayerCluster z [cm]","Energy sum per event [GeV]"),
  #("LayerCluster_x_vs_z",0,z_max,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","x","LayerCluster z [cm]","Average |x| per cluster"),
  #("LayerCluster_y_vs_z",0,z_max,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","y","LayerCluster z [cm]","Average |y| per cluster"),
  #("LayerCluster_energy_integral",0,10,100,"recoCaloClusters_hgcalLayerClustersHSci__GENSIMDIGIRECO","energy","Reconstructed Energy [GeV]","Fraction of events"),
  #("n_MultiClusters",0,10,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","size","Number of MultiClusters","Events"),
  #("MultiCluster_energy",0,5,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","energy","MultiCluster Energy [GeV]","Clusters per event"),
  #("MultiCluster_x",-100,100,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","x","MultiCluster x [cm]","Cluster per events"),
  #("MultiCluster_y",-100,100,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","y","MultiCluster y [cm]","Clusters per event"),
  #("MultiCluster_z",0,z_max,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","z","MultiCluster z [cm]","Clusters per event"),
  #("MultiCluster_energy_vs_z",0,z_max,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","energy","MultiCluster z [cm]","Energy sum per event [GeV]"),
  #("MultiCluster_x_vs_z",0,z_max,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","x","MultiCluster z [cm]","Average |x| per cluster"),
  #("MultiCluster_y_vs_z",0,z_max,100,"recoHGCalMultiClusters_hgcalMultiClusters__GENSIMDIGIRECO","y","MultiCluster z [cm]","Average |y| per cluster"),
    ]
  #histograms=[]
  for l in range(1,layers+1):
    histograms+=[
  #("SimHit_n_integral_in_layer"+str(l),0,1000,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Number of SimHits per layer","Fraction of events"),
  #("SimHit_energy_integral_in_layer"+str(l),0,0.005,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","SimHit energy sum per layer[GeV]","Fraction of events"),
  ("Digi_n_integral_in_layer"+str(l),-0.5,40.5,41,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Number of Digis per layer","Fraction of events"),
  ("Digi_data_integral_in_layer"+str(l),0,2000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per layer","Fraction of events"),
  #("UncalibratedRecHits_n_integral_in_layer"+str(l),0,100,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of RecHits per layer","Fraction of events"),
  #("UncalibratedRecHits_amplitude_integral_in_layer"+str(l),0,100,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of MIP sum per layer","Fraction of events"),
  #("RecHits_n_integral_in_layer"+str(l),0,100,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Number of RecHits per layer","Fraction of events"),
  #("RecHits_energy_integral_in_layer"+str(l),0,5,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Calibrated RecHit Energy sum per layer [GeV]","Fraction of events"),
    ]
  hists={}
  
  events=TChain("Events")
  #events.Add("/data/dust/user/hinzmann/hgcal/8apr2025_th025MIP_10000/gensimdigireco_"+particle.replace("Electron","").replace("Muon","muon")+str(particleEnergy)+".root")
  events.Add("gensimdigireco_"+particle.replace("Electron","electron").replace("Muon","muon")+str(particleEnergy)+stackname+".root")
  i=0
  for event in events:
    if i%100==0: print("event",i)
    i+=1
    for name,xmin,xmax,nbins,branch_name,var,xtitle,ytitle in histograms:
      if not name in hists.keys():
        hists[name]=TH1F(name,name,nbins,xmin,xmax)
      prod=getattr(event,branch_name).product()
      if var=="size":
        hists[name].Fill(len(prod))
      #elif "nanoaod" in branch_name:
      #  for c in range(prod.nColumns()):
      #    if var==prod.columnName(c):
      #      for r in range(prod.nRows()):
      #        hists[name].Fill(prod.getAnyValue(r,c))
      elif "vs" in name:
        for p in prod:
         if "_x_vs_z" in name or "_y_vs_z" in name:
           hists[name].Fill(getattr(p,name.split("_")[-1])(),abs(getattr(p,var)()-160.*("_y_vs_z" in name)))
         elif "vs_layer" in name:
          if "DetIdHGCSampleHGCDataFramesSorted" in branch_name:
           if "outoftime" in name:
            y=sum([getattr(p,var)()[i].data() if i!=2 else 0 for i in range(5)])
           else:
            y=getattr(p,var)()[2].data() # index 2 of 5 time-samples
          else:
           y=getattr(p,var)()
          if "_n_" in name:
           y=1 if y>0 else 0
          
          if "PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO" in branch_name:
           l=layer(p.id())
          else:
           l=layer(p.id().rawId())
          if l>layers: continue
          
          hists[name].Fill(l,y)
         else: 
           if hasattr(p,"z"):
             z=p.z()
             if z-z_offset>z_max: continue
           x=getattr(p,name.split("_")[-1])()
           if "vs_z" in name:
              x-=z_offset
           hists[name].Fill(x,getattr(p,var)())
        if ("_x_vs_z" in name or "_y_vs_z" in name) and len(prod)>0:
          hists[name].Scale(1./len(prod))
      else:
        integral=0
        for p in prod:
         if "data" in var and "DetIdHGCSampleHGCDataFramesSorted" in branch_name:
          if "outoftime" in name:
           x=sum([getattr(p,var)()[i].data() if i!=2 else 0 for i in range(5)])
          else:
           x=getattr(p,var)()[2].data() # index 2 of 5 time-samples
         else:
          x=getattr(p,var)()
         if "_n_" in name:
          x=1 if x>0 else 0

         if hasattr(p,"id"):
           if "PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO" in branch_name:
             l=layer(p.id())
           else:
             l=layer(p.id().rawId())
           if l>layers: continue
           if "in_layer" in name and str(l)!=name.split("_")[-1].strip("layer"): continue
         if hasattr(p,"z"):
           z=p.z()
           if z-z_offset>z_max: continue
         if "_z" in name:
            x-=z_offset
         if "_x" in name:
            x-=x_offset
         if "_y" in name:
            x-=y_offset

         integral+=x
         if not "integral" in name:
          hists[name].Fill(x)
        if "integral" in name:
         hists[name].Fill(integral)

  for name,xmin,xmax,nbins,branch_name,var,xtitle,ytitle in histograms:
    print("plotting", name)
    canvas = TCanvas(name+"_", name+"_", 0, 0, 300, 300)

    if not var=="size":
      hists[name].Scale(1./events.GetEntries())
        
    hists[name].Draw("hist")
    hists[name].SetTitle("")
    hists[name].GetXaxis().SetTitle(xtitle)
    hists[name].GetYaxis().SetTitle(ytitle)
    hists[name].GetXaxis().SetRangeUser(xmin,xmax)
    hists[name].GetYaxis().SetRangeUser(0,hists[name].GetMaximum()*1.1)
    
    l=TLegend(0.6,0.88,0.9,0.9,str(particleEnergy)+" GeV "+particle)
    l.SetFillStyle(0)
    l.SetTextSize(0.05)
    l.Draw("same")
    l2=TLegend(0.6,0.8,0.9,0.9,"Integral: {:.2f}".format(hists[name].Integral()))
    l2.SetFillStyle(0)
    l2.SetTextSize(0.05)
    l2.Draw("same")
    prob=array.array('d',[0.5,0.34,0.68])
    q=array.array('d',[0,0,0])
    hists[name].GetQuantiles(3,q,prob)
    l4=TLegend(0.6,0.75,0.9,0.8,"Median: {:.2f}".format(q[0]))
    l4.SetFillStyle(0)
    l4.SetTextSize(0.05)
    l4.Draw("same")
    if "in_layer" in name:
      l3=TLegend(0.6,0.7,0.9,0.75,"Layer: "+name.split("_")[-1].strip("layer"))
      l3.SetFillStyle(0)
      l3.SetTextSize(0.05)
      l3.Draw("same")
    simulation_output["legend"]=("Integral","Mean","RMS","Median","34% quantile", "68% quantile", "bin edges", "bin content")
    simulation_output[name+"_"+version]=(hists[name].Integral(),hists[name].GetMean(),hists[name].GetStdDev(),q[0],q[1],q[2],
      [hists[name].GetBinLowEdge(b+1) for b in range(hists[name].GetNbinsX())]+[hists[name].GetBinLowEdge(hists[name].GetNbinsX()-1)+hists[name].GetBinWidth(hists[name].GetNbinsX()-1)],
      [hists[name].GetBinContent(b+1) for b in range(hists[name].GetNbinsX())]+[hists[name].GetBinContent(hists[name].GetNbinsX()-1)])

  #// writing the lumi information and the CMS "logo"
  #CMS_lumi( c, iPeriod, iPos );
    
    canvas.SaveAs(name+"_"+version+stackname+".pdf")
    canvas.SaveAs(name+"_"+version+stackname+".root")
    
    #if "LayerCluster_energy_integral" in name:
    if "Digi_data_integral" in name and not "layer" in name:
       pointsX.append(particleEnergy)
       pointsXErr.append(0)
       pointsYresponse.append(hists[name].GetMean())
       pointsYresponseErr.append(hists[name].GetMeanError())
       pointsYresolution.append(hists[name].GetStdDev()/hists[name].GetMean()*100.)
       pointsYresolutionErr.append(hists[name].GetStdDevError()/hists[name].GetMean()*100.)

 print(simulation_output)
 with open("simulation_output"+stackname+".pkl", 'wb') as f:
    pickle.dump(simulation_output, f)

 if len(pointsX)>1:
  canvas = TCanvas("Energy_reconstruction_response", "Energy_reconstruction_response", 0, 0, 300, 300)
  g=TGraphErrors(len(pointsX),pointsX,pointsYresponse,pointsXErr,pointsYresponseErr)
  g.SetMarkerColor(1)
  g.SetMarkerSize(1)
  g.SetLineWidth(2)
  g.SetMarkerStyle(24)
  g.Draw("ap")
  f=TF1("fit","pol1")
  g.Fit(f,"")
  f.Draw("lsame")
  g.SetTitle("")
  g.GetXaxis().SetTitle("Beam energy [GeV]")
  #g.GetYaxis().SetTitle("Reconstructed energy [GeV]")
  g.GetYaxis().SetTitle("ADC count sum")
  canvas.SaveAs("Energy_reconstruction_response"+stackname+".pdf")
  canvas.SaveAs("Energy_reconstruction_response"+stackname+".root")

  canvas = TCanvas("Energy_reconstruction_resolution", "Energy_reconstruction_resolution", 0, 0, 300, 300)
  g=TGraphErrors(len(pointsX),pointsX,pointsYresolution,pointsXErr,pointsYresolutionErr)
  g.SetMarkerColor(1)
  g.SetMarkerSize(1)
  g.SetLineWidth(2)
  g.SetMarkerStyle(24)
  g.Draw("apl")
  g.SetTitle("")
  g.GetXaxis().SetTitle("Beam energy [GeV]")
  g.GetYaxis().SetTitle("Energy resolution [%]")
  canvas.SaveAs("Energy_reconstruction_resolution"+stackname+".pdf")
  canvas.SaveAs("Energy_reconstruction_resolution"+stackname+".root")
