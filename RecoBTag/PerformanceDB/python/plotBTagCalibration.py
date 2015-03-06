#!/usr/bin/env python

import itertools
import os
import shutil
import sys
import dataLoader
import checkBTagCalibrationConsistency as checker
import ROOT


checker.check_coverage = False
ROOT.gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
_rname = ('root_obj_%d' % i for i in xrange(99999999)).next


def _plot_name(sys_token, *eta_pt_discr_bounds):
    name = 'ETA%0.1fto%0.1f_PT%gto%g_DISCR%gto%g' % eta_pt_discr_bounds
    name += '_SYS%s' % (sys_token[1:] if sys_token else 'main')
    name = name.replace('.', 'p')
    return name


def _sort_and_group(entries):
    entries = list(entries)
    if entries[0].params.operatingPoint < 3:
        entries = sorted(entries, key=lambda e: e.params.discrMin)
        entries = sorted(entries, key=lambda e: e.params.etaMin)
        entries = sorted(entries, key=lambda e: e.params.ptMin)
        entries = itertools.groupby(
            entries, lambda e: '%g_%g' % (e.params.etaMin, e.params.discrMin))
        entries = (list(g) for _, g in entries)
    else:
        entries = sorted(entries, key=lambda e: e.params.etaMin)
        entries = sorted(entries, key=lambda e: e.params.ptMin)
        entries = sorted(entries, key=lambda e: e.params.discrMin)
        entries = itertools.groupby(
            entries, lambda e: '%g_%g' % (e.params.etaMin, e.params.ptMin))
        entries = (list(g) for _, g in entries)
    return entries


def plot_canvas(sys_token, ups, ces, dos):
    name = _plot_name(sys_token,
                      ups[0].params.etaMin,
                      ups[0].params.etaMax,
                      ups[0].params.ptMin,
                      ups[-1].params.ptMax,
                      ups[0].params.discrMin,
                      ups[0].params.discrMax)

    if ups[0].params.operatingPoint < 3:
        get_min = lambda e: e.params.ptMin
        get_max = lambda e: e.params.ptMax
    else:
        get_min = lambda e: e.params.discrMin
        get_max = lambda e: e.params.discrMax
    mk_tf1 = lambda e: ROOT.TF1(_rname(), e.formula, get_min(e), get_max(e))

    functions = []

    for up, ce, do in itertools.izip(ups, ces, dos):
        f_up = mk_tf1(up)
        f_ce = mk_tf1(ce)
        f_do = mk_tf1(do)

        functions += [f_up, f_ce, f_do]

        f_up.SetLineWidth(2)
        f_ce.SetLineWidth(3)
        f_do.SetLineWidth(2)

    canv = ROOT.TCanvas(_rname(), '', 600, 600)
    frame = ROOT.TGraph(4)
    frame.SetTitle('')
    frame.SetPoint(1,
                   get_min(ups[0]),
                   0.9*min(f.GetMinimum() for f in functions))
    frame.SetPoint(2,
                   get_max(ups[-1]),
                   1.1*max(f.GetMaximum() for f in functions))
    frame.SetMarkerStyle(1)
    frame.SetMarkerColor(0)
    frame.Draw('AP')

    for f in functions:
        f.Draw('same')

    canv.Modified()
    canv.Update()
    canv.SaveAs(name + '.root')
    canv.SaveAs(name + '.png')


def plot_loader_sys(loader, sys_token):
    entries_up = _sort_and_group(itertools.ifilter(
        lambda e: e.params.sysType == 'up'+sys_token, loader.entries))
    entries_ce = _sort_and_group(itertools.ifilter(
        lambda e: e.params.sysType == 'central', loader.entries))
    entries_do = _sort_and_group(itertools.ifilter(
        lambda e: e.params.sysType == 'down'+sys_token, loader.entries))
    for ens in itertools.izip(entries_up, entries_ce, entries_do):
        plot_canvas(sys_token, *ens)


def plot_loader(loader):
    res = checker.run_check_data([loader], False, True, False)
    if not all(res):
        print 'Checks on csv data failed. Exit.'
        exit(-1)

    sys_tokens = list(s[2:] for s in loader.syss if s.startswith('up'))
    for tok in sys_tokens:
        plot_loader_sys(loader, tok)


def plot(filename):
    loaders = dataLoader.get_data(filename)
    for l in loaders:
        if not l.entries:
            continue
        dirname = 'OP%d_MEAS%s_FLAV%d' % (l.op, l.meas_type, l.flav)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)
        os.chdir(dirname)
        print 'Plotting into directory:', dirname
        print '='*80
        plot_loader(l)
        os.chdir('..')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need csv data file as first argument.'
        exit(-1)

    dataLoader.separate_by_op = dataLoader.separate_by_flav = True
    plot(sys.argv[1])

