# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:24:18 2020

@author: earne
"""
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns

from sipperplots import (
    get_any_idi,
    get_side_idi,
    get_content_idi,
    get_chronogram_vals
        )

def drinkcount_cumulative(sipper, show_left=True, show_right=True,
                          show_content=[], **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    if show_left:
        l = pd.DataFrame({'LeftCount' : df['LeftCount']}, index=df.index)
        output = output.join(l, how='outer')
    if show_right:
        r = pd.DataFrame({'RightCount' : df['RightCount']}, index=df.index)
        output = output.join(r, how='outer')
    if show_content:
        for c in show_content:
            count = sipper.get_content_values(c, out='Count', df=df)
            if not count.empty:
                temp = pd.DataFrame({c +'Count' : count}, index=count.index)
                output = output.join(temp, how='outer')
    return output

def drinkcount_binned(sipper, binsize='1H', show_left=True, show_right=True,
                       show_content=[], **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    base = df.index[0].hour
    if show_left:
        binned = df['LeftCount'].diff().resample(binsize, base=base).sum()
        l = pd.DataFrame({'LeftCount' : binned}, index=binned.index)
        output = output.join(l, how='outer')
    if show_right:
        binned = df['RightCount'].diff().resample(binsize, base=base).sum()
        r = pd.DataFrame({'RightCount' : binned}, index=binned.index)
        output = output.join(r, how='outer')
    if show_content:
        for c in show_content:
            count = sipper.get_content_values(c, out='Count', df=df)
            binned = count.diff().resample(binsize, base=base).sum()
            if not count.empty:
                temp = pd.DataFrame({c+'Count' : binned}, index=binned.index)
                output = output.join(temp, how='outer')
    return output

def drinkduration_cumulative(sipper, show_left=True, show_right=True,
                          show_content=[], **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    if show_left:
        l = pd.DataFrame({'LeftDuration' : df['LeftDuration']}, index=df.index)
        output = output.join(l, how='outer')
    if show_right:
        r = pd.DataFrame({'RightDuration' : df['RightDuration']}, index=df.index)
        output = output.join(r, how='outer')
    if show_content:
        for c in show_content:
            count = sipper.get_content_values(c, out='Count', df=df)
            if not count.empty:
                temp = pd.DataFrame({c+'Duration' : count}, index=count.index)
                output = output.join(temp, how='outer')
    return output

def drinkduration_binned(sipper, binsize='1H', show_left=True, show_right=True,
                       show_content=[], **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    base = df.index[0].hour
    if show_left:
        binned = df['LeftDuration'].diff().resample(binsize, base=base).sum()
        l = pd.DataFrame({'LeftDuration' : binned}, index=binned.index)
        output = output.join(l, how='outer')
    if show_right:
        binned = df['RightDuration'].diff().resample(binsize, base=base).sum()
        r = pd.DataFrame({'RightDuration' : binned}, index=binned.index)
        output = output.join(r, how='outer')
    if show_content:
        for c in show_content:
            count = sipper.get_content_values(c, out='Count', df=df)
            binned = count.diff().resample(binsize, base=base).sum()
            if not count.empty:
                temp = pd.DataFrame({c+'Duration' : binned}, index=binned.index)
                output = output.join(temp, how='outer')
    return output

def interdrink_intervals(sippers, kde=True, logx=True,
                         combine=False, **kwargs):
    if combine:
        output = idi_onecurve(sippers, kde, logx, **kwargs)
    else:
        output = idi_multicurve(sippers, kde, logx, **kwargs)
    return output

def idi_onecurve(sippers, kde, logx, **kwargs):
    bar_df = pd.DataFrame()
    kde_df = pd.DataFrame()
    combined = []
    for sipper in sippers:
        fig = plt.figure()
        plt.clf()
        df = sipper.data.copy()
        if 'date_filter' in kwargs:
            s, e = kwargs['date_filter']
            df = df[(df.index >= s) &
                    (df.index <= e)].copy()
        y = get_any_idi(sipper)
        if logx:
            y = [np.log10(val) for val in y if not pd.isna(val)]
            bins = np.round(np.arange(-2, 5, .1), 2)
        else:
            bins = np.linspace(0, 900, 50)
        combined += list(y)
    plot = sns.distplot(combined, bins=bins, norm_hist=False, kde=kde)
    if kde:
        if plot.get_lines():
            line = plot.get_lines()[0]
            x, y = line.get_data()
            kde_df = kde_df.reindex(x)
            kde_df['Values'] = y
    bar_x = [v.get_x() for v in plot.patches]
    bar_h = [v.get_height() for v in plot.patches]
    bar_df = bar_df.reindex(bar_x)
    bar_df['Values'] = bar_h
    bar_df.index.name = 'log10(minutes)' if logx else 'minutes'
    kde_df.index.name = 'log10(minutes)' if logx else 'minutes'
    plt.close()
    return bar_df, kde_df

def idi_multicurve(sippers, kde, logx, **kwargs):
    bar_df = pd.DataFrame()
    kde_df = pd.DataFrame()
    for sipper in sippers:
        fig = plt.figure()
        plt.clf()
        df = sipper.data.copy()
        if 'date_filter' in kwargs:
            s, e = kwargs['date_filter']
            df = df[(df.index >= s) &
                    (df.index <= e)].copy()
        y = get_any_idi(sipper)
        if logx:
            y = [np.log10(val) for val in y if not pd.isna(val)]
            bins = np.round(np.arange(-2, 5, .1), 2)
        else:
            bins = np.linspace(0, 900, 50)
        plot = sns.distplot(y, bins=bins, norm_hist=False, kde=kde)
        bar_x = [v.get_x() for v in plot.patches]
        bar_h = [v.get_height() for v in plot.patches]
        btemp = pd.DataFrame({sipper.filename : bar_h}, index=bar_x)
        bar_df = bar_df.join(btemp, how='outer')
        if kde:
            if plot.get_lines():
                line = plot.get_lines()[0]
                x, y = line.get_data()
                ktemp = pd.DataFrame({sipper.filename : y}, index=x)
                kde_df = kde_df.join(ktemp, how='outer')
        plt.close()
    bar_df.index.name = 'log10(minutes)' if logx else 'minutes'
    kde_df.index.name = 'log10(minutes)' if logx else 'minutes'
    return bar_df, kde_df

def interdrink_intervals_byside(sippers, kde=True, logx=True, **kwargs):
    bar_df = pd.DataFrame()
    kde_df = pd.DataFrame()
    for side in ['Left', 'Right']:
        combined = []
        fig = plt.figure()
        plt.clf()
        for sipper in sippers:
            df = sipper.data.copy()
            if 'date_filter' in kwargs:
                s, e = kwargs['date_filter']
                df = df[(df.index >= s) &
                        (df.index <= e)].copy()
            y = get_side_idi(sipper, side)
            if logx:
                y = [np.log10(val) for val in y if not pd.isna(val)]
                bins = np.round(np.arange(-2, 5, .1), 2)
            else:
                bins = np.linspace(0, 900, 50)
            combined += list(y)
        plot = sns.distplot(combined, bins=bins, norm_hist=False, kde=kde)
        if kde:
            if plot.get_lines():
                line = plot.get_lines()[0]
                x, y = line.get_data()
                ktemp = pd.DataFrame({side:y}, index=x)
                kde_df = kde_df.join(ktemp, how='outer')
        bar_x = [v.get_x() for v in plot.patches]
        bar_h = [v.get_height() for v in plot.patches]
        btemp = pd.DataFrame({side:bar_h}, index=bar_x)
        bar_df = bar_df.join(btemp, how='outer')
        plt.close()
    bar_df.index.name = 'log10(minutes)' if logx else 'minutes'
    kde_df.index.name = 'log10(minutes)' if logx else 'minutes'
    return bar_df, kde_df

def interdrink_intervals_bycontent(sippers, show_content, kde=True, logx=True,
                                   **kwargs):
    bar_df = pd.DataFrame()
    kde_df = pd.DataFrame()
    for c in show_content:
        combined = []
        fig = plt.figure()
        plt.clf()
        for sipper in sippers:
            df = sipper.data.copy()
            if 'date_filter' in kwargs:
                s, e = kwargs['date_filter']
                df = df[(df.index >= s) &
                        (df.index <= e)].copy()
            y = get_content_idi(sipper, c, df=df)
            if logx:
                y = [np.log10(val) for val in y if not pd.isna(val)]
                bins = np.round(np.arange(-2, 5, .1), 2)
            else:
                bins = np.linspace(0, 900, 50)
            combined += list(y)
        plot = sns.distplot(combined, bins=bins, norm_hist=False, kde=kde)
        if kde:
            if plot.get_lines():
                line = plot.get_lines()[0]
                x, y = line.get_data()
                ktemp = pd.DataFrame({c:y}, index=x)
                kde_df = kde_df.join(ktemp, how='outer')
        bar_x = [v.get_x() for v in plot.patches]
        bar_h = [v.get_height() for v in plot.patches]
        btemp = pd.DataFrame({c:bar_h}, index=bar_x)
        bar_df = bar_df.join(btemp, how='outer')
        plt.close()
    bar_df.index.name = 'log10(minutes)' if logx else 'minutes'
    kde_df.index.name = 'log10(minutes)' if logx else 'minutes'
    return bar_df, kde_df

def drinkcount_chronogram(sipper, circ_left=True, circ_right=True,
                          circ_content=None, lights_on=7,
                          lights_off=19, **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    to_plot = []
    labels = []
    if circ_left:
        to_plot.append(df['LeftCount'])
        labels.append('Left')
    if circ_right:
        to_plot.append(df['RightCount'])
        labels.append('Right')
    if circ_content:
        for c in circ_content:
            vals = sipper.get_content_values(c, 'Count', df=df)
            if not vals.empty:
                to_plot.append()
                labels.append(c)
    for i, series in enumerate(to_plot):
        reindexed = get_chronogram_vals(series, lights_on, lights_off)
        if reindexed.empty:
            continue
        label = labels[i]
        temp = pd.DataFrame({label:reindexed}, index=reindexed.index)
        output = output.join(temp, how='outer')
    output.index.name = 'Hours Into Light Cycle'
    return output

def drinkcount_chronogram_grouped(sippers, groups, circ_left=True, circ_right=True,
                                  circ_content=None, circ_var='SEM', lights_on=7,
                                  lights_off=19, **kwargs):
    output = pd.DataFrame(index=range(0,24))
    output.index.name = 'Hours Into Light Cycle'
    to_plot = defaultdict(list)
    for group in groups:
        for sipper in sippers:
            if group in sipper.groups:
                df = sipper.data
                if 'date_filter' in kwargs:
                    s, e = kwargs['date_filter']
                    df = df[(df.index >= s) &
                            (df.index <= e)].copy()
                if circ_left:
                    key = group + ' - Left'
                    vals = get_chronogram_vals(df['LeftCount'],
                                               lights_on,
                                               lights_off)
                    vals.name = sipper.basename
                    to_plot[key].append(vals)
                if circ_right:
                    key = group + ' - Right'
                    vals = get_chronogram_vals(df['RightCount'],
                                               lights_on,
                                               lights_off)
                    vals.name = sipper.basename
                    to_plot[key].append(vals)
                if circ_content:
                    for c in circ_content:
                        key = group + ' - ' + c
                        content_vals = sipper.get_content_values(c, 'Count', df)
                        if not content_vals.empty:
                            vals = get_chronogram_vals(content_vals,
                                                       lights_on,
                                                       lights_off)
                            vals.name = sipper.basename
                            to_plot[key].append(vals)
    for i, (label, data) in enumerate(to_plot.items()):
        x = range(0,24)
        y = np.nanmean(data, axis=0)
        for d in data:
            output[label + ' - ' + d.name] = d
        output[label + ' MEAN'] = y
        if circ_var == 'SEM':
            sem = stats.sem(data, axis=0, nan_policy='omit')
            output[label + ' SEM'] = sem
        elif circ_var == 'STD':
            std = np.nanstd(data, axis=0)
            output[label + ' STD'] = std
    return output

def drinkduration_chronogram(sipper, circ_left=True, circ_right=True,
                             circ_content=None, lights_on=7,
                             lights_off=19, **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    to_plot = []
    labels = []
    if circ_left:
        to_plot.append(df['LeftDuration'])
        labels.append('Left')
    if circ_right:
        to_plot.append(df['RightDuration'])
        labels.append('Right')
    if circ_content:
        for c in circ_content:
            vals = sipper.get_content_values(c, 'Duration', df=df)
            if not vals.empty:
                to_plot.append()
                labels.append(c)
    for i, series in enumerate(to_plot):
        reindexed = get_chronogram_vals(series, lights_on, lights_off)
        if reindexed.empty:
            continue
        label = labels[i]
        temp = pd.DataFrame({label:reindexed}, index=reindexed.index)
        output = output.join(temp, how='outer')
    output.index.name = 'Hours Into Light Cycle'
    return output

def drinkduration_chronogram_grouped(sippers, groups, circ_left=True, circ_right=True,
                                     circ_content=None, circ_var='SEM', lights_on=7,
                                     lights_off=19, **kwargs):
    output = pd.DataFrame(index=range(0,24))
    output.index.name = 'Hours Into Light Cycle'
    to_plot = defaultdict(list)
    for group in groups:
        for sipper in sippers:
            if group in sipper.groups:
                df = sipper.data
                if 'date_filter' in kwargs:
                    s, e = kwargs['date_filter']
                    df = df[(df.index >= s) &
                            (df.index <= e)].copy()
                if circ_left:
                    key = group + ' - Left'
                    vals = get_chronogram_vals(df['LeftDuration'],
                                               lights_on,
                                               lights_off)
                    vals.name = sipper.basename
                    to_plot[key].append(vals)
                if circ_right:
                    key = group + ' - Right'
                    vals = get_chronogram_vals(df['RightDuration'],
                                               lights_on,
                                               lights_off)
                    vals.name = sipper.basename
                    to_plot[key].append(vals)
                if circ_content:
                    for c in circ_content:
                        key = group + ' - ' + c
                        content_vals = sipper.get_content_values(c, 'Duration', df)
                        if not content_vals.empty:
                            vals = get_chronogram_vals(content_vals,
                                                       lights_on,
                                                       lights_off)
                            vals.name = sipper.basename
                            to_plot[key].append(vals)
    for i, (label, data) in enumerate(to_plot.items()):
        x = range(0,24)
        y = np.nanmean(data, axis=0)
        for d in data:
            output[label + ' - ' + d.name] = d
        output[label + ' MEAN'] = y
        if circ_var == 'SEM':
            sem = stats.sem(data, axis=0, nan_policy='omit')
            output[label + ' SEM'] = sem
        elif circ_var == 'STD':
            std = np.nanstd(data, axis=0)
            output[label + ' STD'] = std
    return output

def side_preference(sipper, pref_side='Left', pref_metric='Count', pref_bins='1H',
                    **kwargs):
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    base = df.index[0].hour
    lcol = 'Left' + pref_metric
    rcol = 'Right' + pref_metric
    l_data = df[lcol].diff().resample(pref_bins, base=base).sum()
    r_data = df[rcol].diff().resample(pref_bins, base=base).sum()
    total = l_data + r_data
    if pref_side == 'Left':
        preference = l_data/total
    else:
        preference = r_data/total
    preference *= 100
    output = pd.DataFrame(preference)
    output.columns = ['{} Preference (% Drink {})'.format(pref_side, pref_metric)]
    return output

def content_preference(sipper, pref_content=[], pref_metric='Count', pref_bins='1H',
                       lights_on=7, lights_off=19, shade_dark=True, **kwargs):
    output = pd.DataFrame()
    df = sipper.data
    if 'date_filter' in kwargs:
        s, e = kwargs['date_filter']
        df = df[(df.index >= s) &
                (df.index <= e)].copy()
    base = df.index[0].hour
    for i, c in enumerate(pref_content):
        target = sipper.get_content_values(c, out=pref_metric, df=df)
        target = target.diff().resample(pref_bins, base=base).sum()
        other  = sipper.get_content_values(c, out=pref_metric, df=df,
                                           opposite=True)
        other = other.diff().resample(pref_bins, base=base).sum()
        if not target.empty and not other.empty:
            preference = target / (target + other) * 100
            temp = pd.DataFrame({c : preference}, index=preference.index)
            output = output.join(temp, how='outer')
    return output