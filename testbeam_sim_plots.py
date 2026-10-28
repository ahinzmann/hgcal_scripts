print("import")

from ROOT import TChain, gROOT, gStyle, TH1F, TCanvas, TLegend, TGraphErrors,TF1,TH2F,TH3F
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

 def phi(id):
   kHGCalPhiOffset = 0
   kHGCalPhiMask = 0x1FF
   return ((int(id) >> kHGCalPhiOffset) & kHGCalPhiMask) 
 
 def ring(id):
   kHGCalRadiusOffset = 9
   kHGCalRadiusMask = 0xFF
   return ((int(id) >> kHGCalRadiusOffset) & kHGCalRadiusMask)
 
 def getLRP(pid):
   l=layer(pid)
   r=ring(pid)
   ph=phi(pid)
   #if l<=4:
   #  r+=1
   #  ph-=103
   #if l>4:
   r-=16
   ph-=67
   return l,r,ph
 
 particle="Electron"
 #particle="PiMinus"
 #particle="Muon"
 #particle="delay0" #noDigi, delay13, delay15, localTime
 stackname="_cernstack_2026Oct28"
 #layers=8 # DESY stack
 layers=15 # CERN stack
 rings=8 # E module
 phis=8 # E module
 x_offset=1 #cm
 y_offset=160 #cm
 z_offset=406.581 #cm (zHGCal6=zHGCalHEmix1)
 z_max=8*4.2 #cm
 veto_tiles=[(1,6,5),
             (2,6,5),
             (3,6,5), 
             (4,6,5), 
             (4,4,5), 
             (5,6,5), 
             (6,6,5), 
             (6,4,2), 
             (7,6,5), 
             (8,6,5), 
             (9,6,5), 
             (9,4,4), 
             (10,6,5), 
             (10,2,4), 
             (11,6,5), 
             (11,3,6), 
             (12,6,5), 
             (12,3,4), 
             (13,6,5), 
             (13,3,4), 
             (14,6,5), 
             (14,3,6), 
             (14,4,4), 
             (14,4,5), 
             (15,6,5), 
             (15,3,6), 
             (15,5,5), 
             ] #layer,ring,phi

 simulation_output={}
 #for particleEnergy in ([1,1.6,2,3,4,5,5.6] if particle=="Electron" else [5]): #[2,3,4,5,6,7,8,9,10] # DESY stack
 for particleEnergy in ([20,100] if particle=="Electron" else( [50,100] if particle=="PiMinus" else [5])): #[2,3,4,5,6,7,8,9,10] # CERN stack
  
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
  gStyle.SetPadRightMargin(0.18)
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

  histograms=[
  #("n_DigisNano",0,100,100,"nanoaodFlatTable_hgcDigiHEbackTable__GENSIMDIGIRECO","size","Number of Digis","Events"),
  #("DigiNano_data",0,500,100,"nanoaodFlatTable_hgcDigiHEbackTable__GENSIMDIGIRECO","data","ADC counts","Hits per event"),
  #("n_Digis",0,100,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","size","Number of Digis","Events"),
  ("Digi_n_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","Number of Digis per layer"),
  #("Digi_n_integral",-0.5,300.5,301,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Number of Digis per event","Fraction of events"),
  #("Digi_data",0,500,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC counts","Hits per event"),
  ("Digi_data_integral",0,200000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per event","Fraction of events"),
  ("Digi_data_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","ADC counts per layer"),
  #("Digi_dataoutoftime",0,500,100,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Out-of-time ADC counts","Hits per event"),
  #("Digi_dataoutoftime_vs_layer",0.5,layers+0.5,layers,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Layer number","Out-of-time ADC counts per layer"),
  #("n_SimHits",0,1000,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","size","Number of SimHits","Events"),
  #("SimHit_n_vs_layer",0.5,layers+0.5,layers,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Layer number","SimHits per layer"),
  #("SimHit_energy",0,0.005,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","SimHit energy [MIP]","Hits per event"),
  ("SimHit_energy_integral",0,400,200,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","SimHit energy [MIP]","Hits per event"),
  ("SimHit_energy_vs_layer",0.5,layers+0.5,layers,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Layer number","SimHit energy per layer [MIP]"),
  #("n_UncalibratedRecHits",0,100,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","size","Number of uncalibrated RecHits","Events"),
  ("UncalibratedRecHits_n_vs_layer",0.5,layers+0.5,layers,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Layer number","Number of RecHits per layer"),
  ("UncalibratedRecHits_amplitude_integral",0,1000,100,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of MIPs","Hits per event"),
  ("UncalibratedRecHits_amplitude_vs_layer",0.5,layers+0.5,layers,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Layer number","Number of MIPs per layer"),
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
  ("Digi_n_integral_in_layer"+str(l),-0.5,40.5,41,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","Number of Digis per layer","Fraction of events"),
  ("Digi_data_integral_in_layer"+str(l),0,20000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per layer","Fraction of events"),
  ("Digi_data_integral_3D_in_layer"+str(l),0,20000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per tile","Fraction of events"),
  #("SimHit_n_integral_in_layer"+str(l),0,1000,100,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","Number of SimHits per layer","Fraction of events"),
  ("SimHit_energy_integral_in_layer"+str(l),0,400,200,"PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO","energy","SimHit energy sum per layer[MIP]","Fraction of events"),
  ("UncalibratedRecHits_n_integral_in_layer"+str(l),0,400,200,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of RecHits per layer","Fraction of events"),
  ("UncalibratedRecHits_amplitude_integral_in_layer"+str(l),0,400,200,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of MIP sum per layer","Fraction of events"),
  ("UncalibratedRecHits_amplitude_integral_3D_in_layer"+str(l),0,400,200,"HGCUncalibratedRecHitsSorted_HGCalUncalibRecHit_HGCHEBUncalibRecHits_GENSIMDIGIRECO","amplitude","Number of MIP sum per layer","Fraction of events"),
  #("RecHits_n_integral_in_layer"+str(l),0,100,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Number of RecHits per layer","Fraction of events"),
  #("RecHits_energy_integral_in_layer"+str(l),0,5,100,"HGCRecHitsSorted_HGCalRecHit_HGCHEBRecHits_GENSIMDIGIRECO","energy","Calibrated RecHit Energy sum per layer [GeV]","Fraction of events"),
    ]
  for l in range(1,layers+1):
    for r in range(1,rings+1):
      for ph in range(1,phis+1):
        histograms+=[
  #("Digi_data_integral_in_layer"+str(l)+"_in_ring"+str(r)+"_in_phi"+str(ph),0,20000,200,"DetIdHGCSampleHGCDataFramesSorted_mix_HGCDigisHEback_GENSIMDIGIRECO","data","ADC count sum per layer","Fraction of events"),
    ]
  hists={}

  files=[]
  #files=["/data/dust/user/hinzmann/hgcal/8apr2025_th025MIP_10000/gensimdigireco_"+particle.replace("Electron","").replace("Muon","muon")+str(particleEnergy)+".root"]
  b="/data/dust/user/hinzmann/hgcal"
  for d in os.listdir(b):
    for f in os.listdir(b+"/"+d):
       if "gensimdigireco_"+particle.replace("Electron","electron").replace("PiMinus","piminus").replace("Muon","muon")+str(particleEnergy)+stackname+".root" in f:
         files+=[b+"/"+d+"/"+f]
         #print("rm "+b+"/"+d+"/"+f)
         pass
  if len(files)==0: 
    files=["gensimdigireco_"+particle.replace("Electron","electron").replace("PiMinus","piminus").replace("Muon","muon")+str(particleEnergy)+stackname+".root"]
  print(files)
  events=TChain("Events")
  for f in files:
    events.Add(f,-1)
  
  i=0
  tree1=[]
  tree2=[]
  tree3=[]
  for event in events:
    if i%100==0: print("event",i)
    i+=1
    for name,xmin,xmax,nbins,branch_name,var,xtitle,ytitle in histograms:
      if not name in hists.keys():
        if "3D" in name:
          hists[name]=TH3F(name,name,phis,0.5,phis+0.5,rings,0.5,rings+0.5,nbins,xmin,xmax)
        else:
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
           y*=1000000.0/455.0 # GeV to MIP
          
          if "PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO" in branch_name:
           l,r,ph=getLRP(p.id())
          else:
           l,r,ph=getLRP(p.id().rawId())
          if l>layers: continue
          if (l,r,ph) in veto_tiles: continue
          
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
        integrals={}
        adc_integrals={}
        tot_integrals={}
        sim_integrals={}
        mip_integrals={}
        for r in range(1,rings+1):
          for ph in range(1,phis+1):
            integrals[str(ph)+str(r)]=0
            for l in range(1,layers+1):
              adc_integrals[str(ph)+str(r)+str(l)]=0
              tot_integrals[str(ph)+str(r)+str(l)]=0
              sim_integrals[str(ph)+str(r)+str(l)]=0
              mip_integrals[str(ph)+str(r)+str(l)]=0
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
         if "PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO" in branch_name:
          x*=1000000.0/455.0 # GeV to MIP

         if hasattr(p,"id"):
           if "PCaloHits_g4SimHits_HGCHitsHEback_GENSIMDIGIRECO" in branch_name:
             l,r,ph=getLRP(p.id())
           else:
             l,r,ph=getLRP(p.id().rawId())
           #print("layer",l)
           #if l==15: print("ring",r)
           #if l==15: print("phi",ph)
           if l>layers: continue
           if (l,r,ph) in veto_tiles: continue
           if "in_layer" in name and str(l)!=name.split("in_layer")[1].split("_")[0]: continue
           if "in_ring" in name and str(r)!=name.split("in_ring")[1].split("_")[0]: continue
           if "in_phi" in name and str(ph)!=name.split("in_phi")[1].split("_")[0]: continue
         if hasattr(p,"z"):
           z=p.z()
           if z-z_offset>z_max: continue
         if "_z" in name:
            x-=z_offset
         if "_x" in name:
            x-=x_offset
         if "_y" in name:
            x-=y_offset

         if name=="Digi_data_integral":
           if str(ph)+str(r)+str(l) in adc_integrals.keys():
             if p[2].mode():
               tot_integrals[str(ph)+str(r)+str(l)]+=x
             else:
               adc_integrals[str(ph)+str(r)+str(l)]+=x
         if name=="UncalibratedRecHits_amplitude_integral":
           if str(ph)+str(r)+str(l) in adc_integrals.keys():
              mip_integrals[str(ph)+str(r)+str(l)]+=x
         if name=="SimHit_energy_integral":
           if str(ph)+str(r)+str(l) in adc_integrals.keys():
              sim_integrals[str(ph)+str(r)+str(l)]+=x
         if "data" in var and "DetIdHGCSampleHGCDataFramesSorted" in branch_name and p[2].mode(): # Treat TOT->ADC
           x*=3.0
         if "3D" in name:
           if str(ph)+str(r) in integrals.keys():
             integrals[str(ph)+str(r)]+=x
         integral+=x
         if not "integral" in name:
          if "3D" in name:
            hists[name].Fill(ph,r,x)
          else:
            hists[name].Fill(x)
        if "integral" in name:
          if name=="Digi_data_integral":
            e=[]
            for r in range(1,rings+1):
              for ph in range(1,phis+1):
                for l in range(1,layers+1):
                  if adc_integrals[str(ph)+str(r)+str(l)]>0 or tot_integrals[str(ph)+str(r)+str(l)]>0:
                    e+=[[l,ph,r,adc_integrals[str(ph)+str(r)+str(l)],tot_integrals[str(ph)+str(r)+str(l)]]]
            tree1+=[[i,e]]
          if name=="UncalibratedRecHits_amplitude_integral":
            e=[]
            for r in range(1,rings+1):
              for ph in range(1,phis+1):
                for l in range(1,layers+1):
                  if mip_integrals[str(ph)+str(r)+str(l)]>0:
                    e+=[l,ph,r,mip_integrals[str(ph)+str(r)+str(l)]]
            tree2+=[[i,e]]
          if name=="SimHit_energy_integral":
            e=[]
            for r in range(1,rings+1):
              for ph in range(1,phis+1):
                for l in range(1,layers+1):
                  if sim_integrals[str(ph)+str(r)+str(l)]>0:
                    e+=[[l,ph,r,sim_integrals[str(ph)+str(r)+str(l)]]]
            tree3+=[[i,e]]
          if "3D" in name:
            for r in range(1,rings+1):
              for ph in range(1,phis+1):
                hists[name].Fill(ph,r,integrals[str(ph)+str(r)])
          else:
            hists[name].Fill(integral)

  print(hists.keys())
  for name,xmin,xmax,nbins,branch_name,var,xtitle,ytitle in histograms:
    print("plotting", name)
    canvas = TCanvas(name+"_", name+"_", 0, 0, 300, 300)

    if not var=="size":
      #hists[name].Scale(1./events.GetEntries())
      pass
        
    if "3D" in name:
      projection=TH2F(name+"2D",name+"2D",phis,0.5,phis+0.5,rings,0.5,rings+0.5)
      for r in range(1,rings+1):
        for ph in range(1,phis+1):
          for i in range(1,hists[name].GetNbinsZ()+1):
            projection.Fill(ph,r,hists[name].GetZaxis().GetBinLowEdge(i)*hists[name].GetBinContent(ph,r,i))
      hists[name]=projection
      hists[name].Draw("COLZ")
      #hists[name].Draw("BOX2")
      hists[name].SetTitle("")
      hists[name].GetXaxis().SetTitle("phi")
      hists[name].GetYaxis().SetTitle("ring")
      hists[name].GetZaxis().SetTitle(xtitle)
      hists[name].GetXaxis().SetRangeUser(0.5,phis+0.5)
      hists[name].GetYaxis().SetRangeUser(0.5,rings+0.5)
      #hists[name].GetZaxis().SetRangeUser(xmin,xmax)
      hists[name].GetZaxis().SetRangeUser(1,hists[name].GetMaximum()*1.1)
    else:
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
    if "3D" in name:
      prob=array.array('d',[0.5,0.34,0.68])
      q={}
      for r in range(1,rings+1):
        for ph in range(1,phis+1):
          q[str(ph)+str(r)]=array.array('d',[0,0,0])
          #hists[name].ProjectionX().GetQuantiles(3,q[str(ph)+str(r)],prob)
    else:
      prob=array.array('d',[0.5,0.34,0.68])
      q=array.array('d',[0,0,0])
      hists[name].GetQuantiles(3,q,prob)
      l4=TLegend(0.6,0.75,0.9,0.8,"Median: {:.2f}".format(q[0]))
      l4.SetFillStyle(0)
      l4.SetTextSize(0.05)
      l4.Draw("same")
    if "in_layer" in name:
      l3=TLegend(0.6,0.7,0.9,0.75,"Layer: "+name.split("in_layer")[1].split("_")[0])
      l3.SetFillStyle(0)
      l3.SetTextSize(0.05)
      l3.Draw("same")
    if "in_ring" in name:
      l3=TLegend(0.6,0.65,0.9,0.7,"Ring: "+name.split("in_ring")[1].split("_")[0])
      l3.SetFillStyle(0)
      l3.SetTextSize(0.05)
      l3.Draw("same")
    if "in_phi" in name:
      l3=TLegend(0.6,0.6,0.9,0.65,"Phi: "+name.split("in_phi")[1].split("_")[0])
      l3.SetFillStyle(0)
      l3.SetTextSize(0.05)
      l3.Draw("same")
    if name=="Digi_data_integral":
      simulation_output[name+"_legend"]=("event",("layer","phi","ring","adc","tot"))
      simulation_output[name+"_"+version]=tree1
      #print(tree)
    elif name=="UncalibratedRecHits_amplitude_integral":
      simulation_output[name+"_legend"]=("event",("layer","phi","ring","mip"))
      simulation_output[name+"_"+version]=tree2
      #print(tree)
    elif name=="SimHit_energy_integral":
      simulation_output[name+"_legend"]=("event",("layer","phi","ring","sim"))
      simulation_output[name+"_"+version]=tree3
      #print(tree)
    elif "3D" in name:
      simulation_output[name+"_legend"]=("phi","ring","bin edges", "bin content")
      simulation_output[name+"_"+version]=[[ph,r,
      [hists[name].GetZaxis().GetBinLowEdge(b+1) for b in range(hists[name].GetNbinsZ())]+[hists[name].GetZaxis().GetBinLowEdge(hists[name].GetNbinsZ()-1)+hists[name].GetZaxis().GetBinWidth(hists[name].GetNbinsZ()-1)],
      [hists[name].GetBinContent(ph+1,r+1,b+1) for b in range(hists[name].GetNbinsZ())]+[hists[name].GetBinContent(ph+1,r+1,hists[name].GetNbinsZ()-1)]]
      for r in range(1,rings+1) for ph in range(1,phis+1)]
    else:
      simulation_output[name+"_legend"]=("Integral","Mean","RMS","Median","34% quantile", "68% quantile", "bin edges", "bin content")
      simulation_output[name+"_"+version]=(hists[name].Integral(),hists[name].GetMean(),hists[name].GetStdDev(),q[0],q[1],q[2],
      [hists[name].GetBinLowEdge(b+1) for b in range(hists[name].GetNbinsX())]+[hists[name].GetBinLowEdge(hists[name].GetNbinsX()-1)+hists[name].GetBinWidth(hists[name].GetNbinsX()-1)],
      [hists[name].GetBinContent(b+1) for b in range(hists[name].GetNbinsX())]+[hists[name].GetBinContent(hists[name].GetNbinsX()-1)])

  #// writing the lumi information and the CMS "logo"
  #CMS_lumi( c, iPeriod, iPos );
    
    canvas.SaveAs(name+"_"+version+stackname+".pdf")
    canvas.SaveAs(name+"_"+version+stackname+".root")
    
    #if "LayerCluster_energy_integral" in name:
    if name=="Digi_data_integral":
       pointsX.append(particleEnergy)
       pointsXErr.append(0)
       pointsYresponse.append(hists[name].GetMean())
       pointsYresponseErr.append(hists[name].GetMeanError())
       pointsYresolution.append(hists[name].GetStdDev()/(max(0.00001,hists[name].GetMean()))*100.)
       pointsYresolutionErr.append(hists[name].GetStdDevError()/(max(0.00001,hists[name].GetMean()))*100.)

  #print(simulation_output)
  with open("simulation_output"+stackname+"_"+particle+".pkl", 'wb') as f:
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
