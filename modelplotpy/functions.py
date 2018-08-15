# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
#from matplotlib.offsetbox import (TextArea, AnnotationBbox)

def plot_response(plot_input, save_fig = True, save_fig_filename = '', highlight_decile = False, highlight_how = 'plot_text'):
    """ Plotting response curve
    
    Parameters
    ----------
    plot_input : pandas dataframe
        The result from scope_modevalplot().
        
    save_fig : bool, default True
        Save the plot.
        
    save_fig_filename : str, default unspecified.
        Specify the path and filetype to save the plot.
        If nothing specified, the plot will be saved as jpeg to the current working directory.
        
    highlight_decile : int, default None
        Highlight the value of the response curve at a specified decile value.
        
    highlight_how : str, plot_text default
        Highlight_how specifies where information about the model performance is printed. It can be shown as text, on the plot or both.
    
    Returns
    -------
    It returns a matplotlib.axes._subplots.AxesSubplot object that can be transformed into the same plot with the .figure command.
    The plot is by default written to disk (save_fig = True). The location and filetype of the file depend on the save_fig_filename parameter.
    If the save_fig_filename parameter is empty (not specified), the plot will be written to the working directory as png. 
    Otherwise the location and file type is specified by the user.
        
    Raises
    ------
    TypeError: If `highlight_decile` is not specified as an int.
    ValueError: If the wrong `highlight_how` value is specified.
    """
    
    models   = plot_input.model_label.unique().tolist()
    datasets = plot_input.dataset_label.unique().tolist()
    classes  = plot_input.target_class.unique().tolist()
    scope = plot_input.scope.unique()[0]
    colors = ("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999")
    
    fig, ax = plt.subplots(figsize = (12,7))
    ax.set_xlabel("decile")
    ax.set_ylabel("response")
    plt.suptitle('Response', fontsize = 16)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xticks(np.arange(1, 11, 1))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.grid(True)
    ax.set_xlim([1, 10])
    ax.set_ylim([0, 1])
    
    if scope == "no_comparison":
        ax.set_title("model: %s & dataset: %s & target class: %s" % (models[0], datasets[0], classes[0]), fontweight = 'bold')
        ax.plot(plot_input.decile, plot_input.pct, label = classes[0], color = colors[0])
        ax.plot(plot_input.decile, plot_input.pct_ref, linestyle = 'dashed', label = "overall response (%s)" % classes[0], color = colors[0])
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_datasets":
        for col, i in enumerate(datasets):
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct[plot_input.dataset_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct_ref[plot_input.dataset_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing datasets & model: %s & target class: %s" % (models[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_models":
        for col, i in enumerate(models):
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct[plot_input.model_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct_ref[plot_input.model_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing models & dataset: %s & target class: %s" % (datasets[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    else: #compare_targetclasses
        for col, i in enumerate(classes):
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct[plot_input.target_class == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct_ref[plot_input.target_class == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("Scope: comparing target classes & dataset: %s & model: %s" % (datasets[0], models[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    
    if highlight_decile != False:
        
        if highlight_decile not in np.linspace(1, 10, num = 10).tolist():
            raise TypeError('Invalid value for highlight_decile parameter. It must be an int value between 1 and 10')
            
        if highlight_how not in ('plot','text','plot_text'):
            raise ValueError('Invalid highlight_how value, it must be one of the following: plot, text or plot_text.')
        
        else:
            text = ''
            if scope == "no_comparison":
                cumpct = plot_input.loc[plot_input.decile == highlight_decile, 'pct'].tolist()
                plt.plot([1, highlight_decile], [cumpct[0]] * 2, linestyle = '-.', color = colors[0], lw = 1.5)
                plt.plot([highlight_decile] * 2 , [0] + [cumpct[0]], linestyle = '-.', color = colors[0], lw = 1.5)
                xy = tuple([highlight_decile] + [cumpct[0]])
                ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[0])
                ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                         textcoords='offset points', ha = 'center', va = 'bottom', color = 'black',
                         bbox=dict(boxstyle='round, pad = 0.4', alpha = 1, fc = colors[0]), #fc = 'yellow', alpha = 0.3),
                         arrowprops = dict(arrowstyle = '->', color = 'black'))
                text += 'When we select decile %d from model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[0], classes[0], int(cumpct[0] * 100)) + '%.\n'
            elif scope == "compare_datasets":
                for col, i in enumerate(datasets):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['dataset_label', 'pct']]
                    cumpct = cumpct.pct[cumpct.dataset_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords='offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox=dict(boxstyle='round, pad = 0.4', alpha = 1, fc = colors[col]), #fc = 'yellow', alpha = 0.3),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select decile %d from model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[col], classes[0], int(cumpct[0] * 100)) + '%.\n'
            elif scope == "compare_models":
                for col, i in enumerate(models):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['model_label', 'pct']]
                    cumpct = cumpct.pct[cumpct.model_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords='offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox=dict(boxstyle='round, pad = 0.4', alpha = 1, fc = colors[col]), #fc = 'yellow', alpha = 0.3),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select decile %d from model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[col], datasets[0], classes[0], int(cumpct[0] * 100)) + '%.\n'
            else: # compare targetvalues
                for col, i in enumerate(classes):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['target_class', 'pct']]
                    cumpct = cumpct.pct[cumpct.target_class == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords='offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox=dict(boxstyle='round, pad = 0.4', alpha = 1, fc = colors[col]), #fc = 'yellow', alpha = 0.3),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select decile %d from model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[0], classes[col], int(cumpct[0] * 100)) + '%.\n'
            if highlight_how in ('text', 'plot_text'):
                print(text[:-1])
            if highlight_how in ('plot', 'plot_text'):
                fig.text(.15, -0.001, text[:-1], ha='left')
    
    if save_fig == True:
        if not save_fig_filename:
            location = '%s/Response chart.png' % os.getcwd()
            plt.savefig(location, dpi = 300)
            print("The response chart is saved in %s" % location)
        else:
            plt.savefig(save_fig_filename, dpi = 300)
            print("The response chart is saved in %s" % save_fig_filename)
        plt.show()
        plt.gcf().clear()
    plt.show()
    return ax

def plot_cumresponse(plot_input, save_fig = True, save_fig_filename = '', highlight_decile = False, highlight_how = 'plot_text'):
    """ Plotting cumulative response curve
    
    Parameters
    ----------
    plot_input : pandas dataframe
        The result from scope_modevalplot().

    save_fig : bool, default True
        Save the plot.

    save_fig_filename : str, default unspecified.
        Specify the path and filetype to save the plot.
        If nothing specified, the plot will be saved as jpeg to the current working directory.

    highlight_decile : int, default None
        Highlight the value of the response curve at a specified decile value.

    highlight_how : str, plot_text default
        Highlight_how specifies where information about the model performance is printed. It can be shown as text, on the plot or both.
        
    Returns
    -------
    It returns a matplotlib.axes._subplots.AxesSubplot object that can be transformed into the same plot with the .figure command.
    The plot is by default written to disk (save_fig = True). The location and filetype of the file depend on the save_fig_filename parameter.
    If the save_fig_filename parameter is empty (not specified), the plot will be written to the working directory as png. 
    Otherwise the location and file type is specified by the user.
        
    Raises
    ------
    TypeError: If `highlight_decile` is not specified as an int.
    ValueError: If the wrong `highlight_how` value is specified.
    """
    models   = plot_input.model_label.unique().tolist()
    datasets = plot_input.dataset_label.unique().tolist()
    classes  = plot_input.target_class.unique().tolist()
    scope = plot_input.scope.unique()[0]
    colors = ("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999")
    
    fig, ax = plt.subplots(figsize = (12,7))
    ax.set_xlabel("decile")
    ax.set_ylabel("cumulative response")
    plt.suptitle('Cumulative response', fontsize = 16)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xticks(np.arange(1, 11, 1))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.grid(True)
    ax.set_xlim([1, 10])
    ax.set_ylim([0, 1])
    
    if scope == "no_comparison":
        ax.set_title("model: %s & dataset: %s & target class: %s" % (models[0], datasets[0], classes[0]), fontweight = 'bold')
        ax.plot(plot_input.decile, plot_input.cumpct, label = classes[0], color = colors[0])
        ax.plot(plot_input.decile, plot_input.pct_ref, linestyle = 'dashed', label = "overall response (%s)" % classes[0], color = colors[0])
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_datasets":
        for col, i in enumerate(datasets):
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumpct[plot_input.dataset_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct_ref[plot_input.dataset_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing datasets & model: %s & target class: %s" % (models[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_models":
        for col, i in enumerate(models):
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumpct[plot_input.model_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct_ref[plot_input.model_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("Scope: comparing models & dataset: %s & target class: %s" % (datasets[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    else: #compare_targetclasses
        for col, i in enumerate(classes):
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumpct[plot_input.target_class == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct_ref[plot_input.target_class == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("Comparing target classes & dataset: %s & model: %s" % (datasets[0], models[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    
    if highlight_decile != False:
        
        if highlight_decile not in np.linspace(1, 10, num = 10).tolist():
            raise TypeError('Invalid value for highlight_decile parameter. It must be an int value between 1 and 10')
            
        if highlight_how not in ('plot','text','plot_text'):
            raise ValueError('Invalid highlight_how value, it must be one of the following: plot, text or plot_text.')
        
        else:
            text = ''
            if scope == "no_comparison":
                cumpct = plot_input.loc[plot_input.decile == highlight_decile, 'cumpct'].tolist()
                plt.plot([1, highlight_decile], [cumpct[0]] * 2, linestyle = '-.', color = colors[0], lw = 1.5)
                plt.plot([highlight_decile] * 2 , [0] + [cumpct[0]], linestyle = '-.', color = colors[0], lw = 1.5)
                xy = tuple([highlight_decile] + [cumpct[0]])
                ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[0])
                ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                         textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                         bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[0]),
                         arrowprops = dict(arrowstyle = '->', color = 'black'))
                text += 'When we select deciles 1 until %d according to model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[0], classes[0], int(cumpct[0] * 100)) + '%.\n'
            elif scope == "compare_datasets":
                for col, i in enumerate(datasets):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['dataset_label', 'cumpct']]
                    cumpct = cumpct.cumpct[cumpct.dataset_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select deciles 1 until %d according to model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[col], classes[0], int(cumpct[0] * 100)) + '%.\n'
            elif scope == "compare_models":
                for col, i in enumerate(models):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['model_label', 'cumpct']]
                    cumpct = cumpct.cumpct[cumpct.model_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select deciles 1 until %d according to model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[col], datasets[0], classes[0], int(cumpct[0] * 100)) + '%.\n'
            else: # compare targetvalues
                for col, i in enumerate(classes):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['target_class', 'cumpct']]
                    cumpct = cumpct.cumpct[cumpct.target_class == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select deciles 1 until %d according to model %s in dataset %s the percentage of %s cases in the selection is %d' % (highlight_decile, models[0], datasets[0], classes[col], int(cumpct[0] * 100)) + '%.\n'
            
            if highlight_how in ('text', 'plot_text'):
                print(text[:-1])
            if highlight_how in ('plot', 'plot_text'):
                fig.text(.15, -0.001, text[:-1], ha='left')
                    
    if save_fig == True:
        if not save_fig_filename:
            location = '%s/Cumulative response chart.png' % os.getcwd()
            plt.savefig(location, dpi = 300)
            print("The cumulative response chart is saved in %s" % location)
        else:
            plt.savefig(save_fig_filename, dpi = 300)
            print("The cumulative response chart is saved in %s" % save_fig_filename)
        plt.show()
        plt.gcf().clear()
    plt.show()
    return ax

def plot_cumlift(plot_input, save_fig = True, save_fig_filename = '', highlight_decile = False, highlight_how = 'plot_text'):
    """ Plotting cumulative lift curve
    
    Parameters
    ----------
    plot_input : pandas dataframe
        The result from scope_modevalplot().

    save_fig : bool, default True
        Save the plot.

    save_fig_filename : str, default unspecified.
        Specify the path and filetype to save the plot.
        If nothing specified, the plot will be saved as jpeg to the current working directory.

    highlight_decile : int, default None
        Highlight the value of the response curve at a specified decile value.

    highlight_how : str, plot_text default
        Highlight_how specifies where information about the model performance is printed. It can be shown as text, on the plot or both.
    
    Returns
    -------
    It returns a matplotlib.axes._subplots.AxesSubplot object that can be transformed into the same plot with the .figure command.
    The plot is by default written to disk (save_fig = True). The location and filetype of the file depend on the save_fig_filename parameter.
    If the save_fig_filename parameter is empty (not specified), the plot will be written to the working directory as png. 
    Otherwise the location and file type is specified by the user.
        
    Raises
    ------
    TypeError: If `highlight_decile` is not specified as an int.
    ValueError: If the wrong `highlight_how` value is specified.
    """
    models   = plot_input.model_label.unique().tolist()
    datasets = plot_input.dataset_label.unique().tolist()
    classes  = plot_input.target_class.unique().tolist()
    scope = plot_input.scope.unique()[0]
    colors = ("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999")

    fig, ax = plt.subplots(figsize = (12,7))
    ax.set_xlabel("decile")
    ax.set_ylabel("cumulative lift")
    plt.suptitle('Cumulative lift', fontsize = 16)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xticks(np.arange(1, 11, 1))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.grid(True)
    ax.set_xlim([1, 10])
    ax.set_ylim([0, max(plot_input.cumlift)])
    ax.plot(list(range(1, 11, 1)), [1] * 10, linestyle = 'dashed', label = "no lift", color = 'grey')
    
    if scope == "no_comparison":
        ax.set_title("model: %s & dataset: %s & target class: %s" % (models[0], datasets[0], classes[0]), fontweight = 'bold')
        ax.plot(plot_input.decile, plot_input.cumlift, label = classes[0], color = colors[0])
        #ax.plot(plot_input.decile, plot_input.cumlift_ref, linestyle = 'dashed', label = "overall response (%s)" % classes[0], color = colors[0])
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_datasets":
        for col, i in enumerate(datasets):
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumlift[plot_input.dataset_label == i], label = i, color = colors[col])
            #ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumlift_ref[plot_input.dataset_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing datasets & model: %s & target class: %s" % (models[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_models":
        for col, i in enumerate(models):
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumlift[plot_input.model_label == i], label = i, color = colors[col])
            #ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumlift_ref[plot_input.model_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing models & dataset: %s & target class: %s" % (datasets[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    else: #compare_targetclasses
        for col, i in enumerate(classes):
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumlift[plot_input.target_class == i], label = i, color = colors[col])
            #ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumlift_ref[plot_input.target_class == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax.set_title("scope: comparing target classes & dataset: %s & model: %s" % (datasets[0], models[0]), fontweight = 'bold')
        ax.legend(loc = 'upper right', shadow = False, frameon = False)
    
    if highlight_decile != False:
        
        if highlight_decile not in np.linspace(1, 10, num = 10).tolist():
            raise TypeError('Invalid value for highlight_decile parameter. It must be an int value between 1 and 10')
            
        if highlight_how not in ('plot','text','plot_text'):
            raise ValueError('Invalid highlight_how value, it must be one of the following: plot, text or plot_text.')
        
        else:
            text = ''
            if scope == "no_comparison":
                cumpct = plot_input.loc[plot_input.decile == highlight_decile, 'cumlift'].tolist()
                plt.plot([1, highlight_decile], [cumpct[0]] * 2, linestyle = '-.', color = colors[0], lw = 1.5)
                plt.plot([highlight_decile] * 2 , [0] + [cumpct[0]], linestyle = '-.', color = colors[0], lw = 1.5)
                xy = tuple([highlight_decile] + [cumpct[0]])
                ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[0])
                ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                         textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                         bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[0]),
                         arrowprops = dict(arrowstyle = '->', color = 'black'))
                text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s in dataset %s, this selection for target class %s is %s times than selecting without a model.\n' % (models[0], datasets[0], classes[0], str(round(cumpct[0], 2)))
            elif scope == "compare_datasets":
                for col, i in enumerate(datasets):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['dataset_label', 'cumlift']]
                    cumpct = cumpct.cumlift[cumpct.dataset_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s in dataset %s, this selection for target class %s is %s times than selecting without a model.\n' % (models[0], datasets[col], classes[0], str(round(cumpct[0], 2)))
            elif scope == "compare_models":
                for col, i in enumerate(models):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['model_label', 'cumlift']]
                    cumpct = cumpct.cumlift[cumpct.model_label == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s in dataset %s, this selection for target class %s is %s times than selecting without a model.\n' % (models[col], datasets[0], classes[0], str(round(cumpct[0], 2)))
            else: # compare targetvalues
                for col, i in enumerate(classes):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['target_class', 'cumlift']]
                    cumpct = cumpct.cumlift[cumpct.target_class == i].tolist()
                    plt.plot([1, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s in dataset %s, this selection for target class %s is %s times than selecting without a model.\n' % (models[0], datasets[0], classes[col], str(round(cumpct[0], 2)))
            
            if highlight_how in ('text', 'plot_text'):
                print(text[:-1])
            if highlight_how in ('plot', 'plot_text'):
                fig.text(.15, -0.001, text[:-1], ha='left')
    
    if save_fig == True:
        if not save_fig_filename:
            location = '%s/Cumulative lift chart.png' % os.getcwd()
            plt.savefig(location, dpi = 300)
            print("The cumulative lift chart is saved in %s" % location)
        else:
            plt.savefig(save_fig_filename, dpi = 300)
            print("The cumulative lift chart is saved in %s" % save_fig_filename)
        plt.show()
        plt.gcf().clear()
    plt.show()
    return ax

def plot_cumgains(plot_input, save_fig = True, save_fig_filename = '', highlight_decile = False, highlight_how = 'plot_text'):
    """ Plotting cumulative gains curve
    
    Parameters
    ----------
    plot_input : pandas dataframe
        The result from scope_modevalplot().

    save_fig : bool, default True
        Save the plot.

    save_fig_filename : str, default unspecified.
        Specify the path and filetype to save the plot.
        If nothing specified, the plot will be saved as jpeg to the current working directory.

    highlight_decile : int, default None
        Highlight the value of the response curve at a specified decile value.
    
    highlight_how : str, plot_text default
        Highlight_how specifies where information about the model performance is printed. It can be shown as text, on the plot or both.
    
    Returns
    -------
    It returns a matplotlib.axes._subplots.AxesSubplot object that can be transformed into the same plot with the .figure command.
    The plot is by default written to disk (save_fig = True). The location and filetype of the file depend on the save_fig_filename parameter.
    If the save_fig_filename parameter is empty (not specified), the plot will be written to the working directory as png. 
    Otherwise the location and file type is specified by the user.
        
    Raises
    ------
    TypeError: If `highlight_decile` is not specified as an int.
    ValueError: If the wrong `highlight_how` value is specified.
    """
    models   = plot_input.model_label.unique().tolist()
    datasets = plot_input.dataset_label.unique().tolist()
    classes  = plot_input.target_class.unique().tolist()
    scope = plot_input.scope.unique()[0]
    colors = ("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999")
    
    fig, ax = plt.subplots(figsize = (12,7))
    ax.set_xlabel("decile")
    ax.set_ylabel("cumulative gains")
    plt.suptitle('Cumulative gains', fontsize = 16)
    ax.set_xticks(np.arange(0, 11, 1))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.plot(list(range(0, 11, 1)), np.linspace(0, 1, num = 11).tolist(), linestyle = 'dashed', label = "minimal gains", color = 'grey')
    ax.grid(True)
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 1])
    
    if scope == "no_comparison":
        ax.set_title("model: %s & dataset: %s & target class: %s" % (models[0], datasets[0], classes[0]), fontweight = 'bold')
        ax.plot(plot_input.decile, plot_input.cumgain, label = classes[0], color = colors[0])
        ax.plot(plot_input.decile, plot_input.gain_opt, linestyle = 'dashed', label = "optimal gains (%s)" % classes[0], color = colors[0], linewidth = 1.5)
        ax.legend(loc = 'lower right', shadow = False, frameon = False)
    elif scope == "compare_datasets":
        for col, i in enumerate(datasets):
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumgain[plot_input.dataset_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.gain_opt[plot_input.dataset_label == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col], linewidth = 1.5)
        ax.set_title("scope: comparing datasets & model: %s & target class: %s" % (models[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'lower right', shadow = False, frameon = False)
    elif scope == "compare_models":
        for col, i in enumerate(models):
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumgain[plot_input.model_label == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.model_label == i], plot_input.gain_opt[plot_input.model_label == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col], linewidth = 1.5)
        ax.set_title("scope: comparing models & dataset: %s & target class: %s" % (datasets[0], classes[0]), fontweight = 'bold')
        ax.legend(loc = 'lower right', shadow = False, frameon = False)
    else: #compare_targetclasses
        for col, i in enumerate(classes):
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumgain[plot_input.target_class == i], label = i, color = colors[col])
            ax.plot(plot_input.decile[plot_input.target_class == i], plot_input.gain_opt[plot_input.target_class == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col], linewidth = 1.5)
        ax.set_title("scope: comparing target classes & dataset: %s & model: %s" % (datasets[0], models[0]), fontweight = 'bold')
        ax.legend(loc = 'lower right', shadow = False, frameon = False)
    
    if highlight_decile != False:
        
        if highlight_decile not in np.linspace(1, 10, num = 10).tolist():
            raise TypeError('Invalid value for highlight_decile parameter. It must be an int value between 1 and 10')
            
        if highlight_how not in ('plot','text','plot_text'):
            raise ValueError('Invalid highlight_how value, it must be one of the following: plot, text or plot_text.')
        
        else:
            text = ''
            if scope == "no_comparison":
                cumpct = plot_input.loc[plot_input.decile == highlight_decile, 'cumgain'].tolist()
                plt.plot([0, highlight_decile], [cumpct[0]] * 2, linestyle = '-.', color = colors[0], lw = 1.5)
                plt.plot([highlight_decile] * 2 , [0] + [cumpct[0]], linestyle = '-.', color = colors[0], lw = 1.5)
                xy = tuple([highlight_decile] + [cumpct[0]])
                ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[0])
                ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                         textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                         bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[0]),
                         arrowprops = dict(arrowstyle = '->', color = 'black'))
                text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s, this selection holds %d' % (models[0], int(cumpct[0] * 100)) + '%' + ' of all %s cases in dataset %s.\n'  % (classes[0], datasets[0])
            elif scope == "compare_datasets":
                for col, i in enumerate(datasets):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['dataset_label', 'cumgain']]
                    cumpct = cumpct.cumgain[cumpct.dataset_label == i].tolist()
                    plt.plot([0, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s, this selection holds %d' % (models[0], int(cumpct[0] * 100)) + '%' + ' of all %s cases in dataset %s.\n'  % (classes[0], datasets[col])
            elif scope == "compare_models":
                for col, i in enumerate(models):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['model_label', 'cumgain']]
                    cumpct = cumpct.cumgain[cumpct.model_label == i].tolist()
                    plt.plot([0, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s, this selection holds %d' % (models[col], int(cumpct[0] * 100)) + '%' + ' of all %s cases in dataset %s.\n'  % (classes[0], datasets[0])
            else: # compare targetvalues
                for col, i in enumerate(classes):
                    cumpct = plot_input.loc[plot_input.decile == highlight_decile, ['target_class', 'cumgain']]
                    cumpct = cumpct.cumgain[cumpct.target_class == i].tolist()
                    plt.plot([0, highlight_decile], cumpct * 2, linestyle = '-.', color = colors[col], lw = 1.5)
                    plt.plot([highlight_decile] * 2, [0] + cumpct, linestyle = '-.', color = colors[col], lw = 1.5)
                    xy = tuple([highlight_decile] + cumpct)
                    ax.plot(xy[0], xy[1], ".r", ms = 20, color = colors[col])
                    ax.annotate(str(int(cumpct[0] * 100)) + "%", xy = xy, xytext = (-30, -30), 
                             textcoords = 'offset points', ha = 'center', va = 'bottom', color = 'black',
                             bbox = dict(boxstyle = 'round, pad = 0.4', alpha = 1, fc = colors[col]),
                             arrowprops = dict(arrowstyle = '->', color = 'black'))
                    text += 'When we select %d' % (highlight_decile * 10) + '%' + ' with the highest probability according to model %s, this selection holds %d' % (models[0], int(cumpct[0] * 100)) + '%' + ' of all %s cases in dataset %s.\n'  % (classes[col], datasets[0])
            
            if highlight_how in ('text', 'plot_text'):
                print(text[:-1])
            if highlight_how in ('plot', 'plot_text'):
                fig.text(.15, -0.001, text[:-1], ha='left')
    
    if save_fig == True:
        if not save_fig_filename:
            location = '%s/Cumulative gains chart.png' % os.getcwd()
            plt.savefig(location, dpi = 300)
            print("The cumulative gains chart is saved in %s" % location)
        else:
            plt.savefig(save_fig_filename, dpi = 300)
            print("The cumulative gains chart is saved in %s" % save_fig_filename)
        plt.show()
        plt.gcf().clear()
    plt.show()
    return ax

def plot_all(plot_input, save_fig = True, save_fig_filename = ''):
    """ Plotting cumulative gains curve

    Parameters
    ----------
    plot_input : pandas dataframe
        The result from scope_modevalplot().

    save_fig : bool, default True
        Save the plot.

    save_fig_filename : str, default unspecified.
        Specify the path and filetype to save the plot.
        If nothing specified, the plot will be saved as jpeg to the current working directory.

    Returns
    -------
    It returns a matplotlib.axes._subplots.AxesSubplot object that can be transformed into the same plot with the .figure command.
    The plot is by default written to disk (save_fig = True). The location and filetype of the file depend on the save_fig_filename parameter.
    If the save_fig_filename parameter is empty (not specified), the plot will be written to the working directory as png. 
    Otherwise the location and file type is specified by the user.
    """
    models   = plot_input.model_label.unique().tolist()
    datasets = plot_input.dataset_label.unique().tolist()
    classes  = plot_input.target_class.unique().tolist()
    scope = plot_input.scope.unique()[0]
    colors = ("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex = False, sharey = False, figsize = (15,10))
    #plt.text(x=0.5, y=0.94, s="4 evaluation charts", fontsize=18, ha="center", transform=fig.transFigure)

    ax1.set_title('Cumulative gains', fontweight='bold')
    ax1.set_ylabel('cumulative gains')
    #ax1.set_xlabel('decile')
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax1.set_xticks(np.arange(0, 11, 1))
    ax1.set_ylim(0, 1)
    ax1.set_xlim(0, 10)
    ax1.set_xticks(np.arange(0, 11, 1))
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(True)
    ax1.yaxis.set_ticks_position('left')
    ax1.xaxis.set_ticks_position('bottom')
    ax1.plot(list(range(0, 11, 1)), np.linspace(0, 1, num = 11).tolist(), linestyle = 'dashed', label = "minimal gains", color = 'grey')

    ax2.set_title('Cumulative lift', fontweight='bold')
    ax2.set_ylabel('cumulative lift')
    #ax2.set_xlabel('decile')
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax2.set_xticks(np.arange(1, 11, 1))
    ax2.set_xlim(1, 10)
    ax2.set_ylim([0, max(plot_input.cumlift)])
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.grid(True)
    ax2.yaxis.set_ticks_position('left')
    ax2.xaxis.set_ticks_position('bottom')
    ax2.plot(list(range(1, 11, 1)), [1] * 10, linestyle = 'dashed', label = "no lift", color = 'grey')

    ax3.set_title('Response', fontweight='bold')
    ax3.set_ylabel('response')
    ax3.set_xlabel('decile')
    ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax3.set_xticks(np.arange(1, 11, 1))
    ax3.set_xlim(1, 10)
    ax3.set_ylim(0, 1)
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax3.grid(True)
    ax3.yaxis.set_ticks_position('left')
    ax3.xaxis.set_ticks_position('bottom')
    
    ax4.set_title('Cumulative response', fontweight='bold')
    ax4.set_ylabel('cumulative response')
    ax4.set_xlabel('decile')
    ax4.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax4.set_xticks(np.arange(1, 11, 1))
    ax4.set_xlim(1, 10)
    ax4.set_ylim(0, 1)
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)
    ax4.grid(True)
    ax4.yaxis.set_ticks_position('left')
    ax4.xaxis.set_ticks_position('bottom')
    
    if scope == "no_comparison":
        title = "model: %s & dataset: %s & target class: %s" % (models[0], datasets[0], classes[0])
        ax1.plot(plot_input.decile, plot_input.cumgain, label = classes[0], color = colors[0])
        ax1.plot(plot_input.decile, plot_input.gain_opt, linestyle = 'dashed', label = "optimal gains (%s)" % classes[0], color = colors[0])
        ax1.legend(loc = 'lower right', shadow = False, frameon = False)
        ax2.plot(plot_input.decile, plot_input.cumlift, label = classes[0], color = colors[0])
        ax2.legend(loc = 'upper right', shadow = False, frameon = False)
        ax3.plot(plot_input.decile, plot_input.pct, label = classes[0], color = colors[0])
        ax3.plot(plot_input.decile, plot_input.pct_ref, linestyle = 'dashed', label = "overall response (%s)" % classes[0], color = colors[0])
        ax3.legend(loc = 'upper right', shadow = False, frameon = False)
        ax4.plot(plot_input.decile, plot_input.cumpct, label = classes[0], color = colors[0])
        ax4.plot(plot_input.decile, plot_input.pct_ref, linestyle = 'dashed', label = "overall response (%s)" % classes[0], color = colors[0])
        ax4.legend(loc = 'upper right', shadow = False, frameon = False)
    elif scope == "compare_datasets":
        title = "scope: comparing datasets & model: %s & target class: %s" % (models[0], classes[0])
        for col, i in enumerate(datasets):
            ax1.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumgain[plot_input.dataset_label == i], label = i, color = colors[col])
            ax1.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.gain_opt[plot_input.dataset_label == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col])
            ax2.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumlift[plot_input.dataset_label == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct[plot_input.dataset_label == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct_ref[plot_input.dataset_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.cumpct[plot_input.dataset_label == i], label = i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.dataset_label == i], plot_input.pct_ref[plot_input.dataset_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax1.legend(loc = 'lower right', shadow = False, frameon = False)
        ax2.legend(loc = 'upper right', shadow = False, frameon = False)
        ax3.legend(loc = 'upper right', shadow = False, frameon = False)
        ax4.legend(loc = 'upper right', shadow = False, frameon = False)        
    elif scope == "compare_models":
        title = "scope: comparing models & dataset: %s & target class: %s" % (datasets[0], classes[0])
        for col, i in enumerate(models):
            ax1.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumgain[plot_input.model_label == i], label = i, color = colors[col])
            ax1.plot(plot_input.decile[plot_input.model_label == i], plot_input.gain_opt[plot_input.model_label == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col])
            ax2.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumlift[plot_input.model_label == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct[plot_input.model_label == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct_ref[plot_input.model_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.model_label == i], plot_input.cumpct[plot_input.model_label == i], label = i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.model_label == i], plot_input.pct_ref[plot_input.model_label == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])            
        ax1.legend(loc = 'lower right', shadow = False, frameon = False)
        ax2.legend(loc = 'upper right', shadow = False, frameon = False)
        ax3.legend(loc = 'upper right', shadow = False, frameon = False)
        ax4.legend(loc = 'upper right', shadow = False, frameon = False)
    else: #compare_targetclasses
        title = "scope: comparing target classes & dataset: %s & model: %s" % (datasets[0], models[0])
        for col, i in enumerate(classes):
            ax1.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumgain[plot_input.target_class == i], label = i, color = colors[col])
            ax1.plot(plot_input.decile[plot_input.target_class == i], plot_input.gain_opt[plot_input.target_class == i], linestyle = 'dashed', label = "optimal gains (%s)" % i, color = colors[col])
            ax2.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumlift[plot_input.target_class == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct[plot_input.target_class == i], label = i, color = colors[col])
            ax3.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct_ref[plot_input.target_class == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.target_class == i], plot_input.cumpct[plot_input.target_class == i], label = i, color = colors[col])
            ax4.plot(plot_input.decile[plot_input.target_class == i], plot_input.pct_ref[plot_input.target_class == i], linestyle = 'dashed', label = "overall response (%s)" % i, color = colors[col])
        ax1.legend(loc = 'lower right', shadow = False, frameon = False)
        ax2.legend(loc = 'upper right', shadow = False, frameon = False)
        ax3.legend(loc = 'upper right', shadow = False, frameon = False)
        ax4.legend(loc = 'upper right', shadow = False, frameon = False)
    plt.suptitle(title, fontsize = 16)
    if save_fig == True:
        if not save_fig_filename:
            location = '%s/Plot all.png' % os.getcwd()
            plt.savefig(location, dpi = 300)
            print("The multi plot object is saved in %s" % location)
        else:
            plt.savefig(save_fig_filename, dpi = 300)
            print("The multi plot object is saved in %s" % save_fig_filename)
        plt.show()
        plt.gcf().clear()
    plt.show()
    return ax1

def range01(x):
    """ Normalizing input
    
    Parameters
    ----------
    x : list of numeric data
        List of numeric data to get normalized

    Returns
    -------
    normalized version of x
    
    """
    return (x-np.min(x))/(np.max(x)-np.min(x))

def check_input(input_list, check_list, check = ''):
    """ Check if the input matches any of a complete list
    
    Parameters
    ----------
    input_list : list of str
        List containing elements specified by the user.

    check_list : list of str
        List containing all possible elements defined by the model_plots object.

    check : str, default empty
        String contains the parameter that will be checked to provide an informative error.

    Returns
    -------
    error if there is no match with the complete list or the input list again
        
    Raises
    ------
    ValueError: If the elements in `input list` do not correspond with the `check_lisk`.

    """
    if len(input_list) >= 1:
        if any(elem in input_list for elem in check_list):
            input_list = input_list
        else:
            raise ValueError('Invalid input for parameter %s. The input for %s is 1 or more elements from %s and put in a list.' % (check, check, check_list))
    return list(input_list)

class modelplotpy(object):
    """ Create a model_plots object
    
    Parameters
    ----------    
    feature_data : list of objects
        Objects containing the X matrix for one or more different datasets.

    label_data : list of objects 
        Objects of the y vector for one or more different datasets.

    dataset_labels : list of str 
        Containing the names of the different `feature_data` and `label_data` combination pairs.

    models : list of objects
        Containing the sk-learn model objects

    model_labels : list of str
        Names of the (sk-learn) models

    seed : int, default 999
        Make results reproducible, in the case of a small dataset the data cannot be split into 10 unique deciles.

    Raises
    ------
    ValueError: If there is no match with the complete list or the input list again

    """

    def __init__(self, feature_data = [], label_data = [], dataset_labels = [], models = [], model_labels = [], seed = 999):
        """ Create a model_plots object

        Parameters
        ----------
        feature_data : list of objects
            Objects containing the X matrix for one or more different datasets.
            
        label_data : list of objects 
            Objects of the y vector for one or more different datasets.
            
        dataset_labels : list of str 
            Containing the names of the different `feature_data` and `label_data` combination pairs.
        
        models : list of objects
            Containing the sk-learn model objects
        
        model_labels : list of str
            Names of the (sk-learn) models
            
        seed : int, default 999
            Make results reproducible, in the case of a small dataset the data cannot be split into 10 unique deciles.

        Raises
        ------
        ValueError: If there is no match with the complete list or the input list again

        """
        self.feature_data = feature_data
        self.label_data = label_data
        self.dataset_labels = dataset_labels
        self.models = models
        self.model_labels = model_labels
        self.seed = seed

    def prepare_scores_and_deciles(self):
        """ Create eval_tot
        
        This function builds the pandas dataframe eval_tot that contains for each feature and label data pair given a description the actual and predicted value.
        It loops over the different models with the given model_name.
        
        Parameters
        ----------
        feature_data : list of objects
            Objects containing the X matrix for one or more different datasets.
            
        label_data : list of objects 
            Objects of the y vector for one or more different datasets.
            
        dataset_labels : list of str 
            Containing the names of the different feature `feature_data` and label `label_data` data combination pairs.
        
        models : list of objects
            Containing the sk-learn model objects
        
        model_labels : list of str
            Names of the (sk-learn) models
            
        seed : int, default 999
            Make results reproducible, in the case of a small dataset the data cannot be split into 10 unique deciles.

        Returns
        -------
        Pandas dataframe for all given information and for each target_class it makes a prediction and decile.
        For each decile a small value (based on the seed) is added and normalized to make the results reproducible.

        Raises
        ------
        ValueError: If there is no match with the complete list or the input list again
        """
        if (len(self.models) == len(self.model_labels)) == False:
            raise ValueError('The number of models and the their description model_name must be equal. The number of model = %s and model_name = %s.' % (len(self.model), len(self.model_name)) )

        if (len(self.feature_data) == len(self.label_data) == len(self.dataset_labels)) == False:
            raise ValueError('The number of datasets in feature_data and label_data and their description pairs must be equal. The number of datasets in feature_data = %s, label_data = %s and description = %s.' % (len(self.feature_data), len(self.label_data), len(self.description)))
        
        final = pd.DataFrame()
        for i in range(len(self.models)):
            data_set = pd.DataFrame()
            for j in range(len(self.dataset_labels)):
                y_true = self.label_data[j]
                y_true = y_true.rename('target_class')
                # probabilities and rename them
                y_pred = self.models[i].predict_proba(self.feature_data[j])
                probabilities = pd.DataFrame(data = y_pred, index = self.feature_data[j].index)
                probabilities.columns = 'prob_' + self.models[i].classes_
                # combine the datasets
                dataset = pd.concat([self.feature_data[j], probabilities, y_true], axis = 1, join_axes = [self.feature_data[j].index])
                dataset['dataset_label'] = self.dataset_labels[j]
                dataset['model_label'] = self.model_labels[i]
                # remove the feature columns
                dataset = dataset.drop(list(self.feature_data[j].columns), axis=1)
                # make deciles
                # loop over different outcomes
                n = dataset.shape[0]
                for k in self.models[i].classes_:
                    #! Added small proportion to prevent equal decile bounds and reset to 0-1 range (to prevent probs > 1.0)
                    np.random.seed(self.seed)
                    prob_plus_smallrandom = range01(dataset[['prob_' + k]] + (np.random.uniform(size = (n, 1)) / 1000000))
                    prob_plus_smallrandom = np.array(prob_plus_smallrandom['prob_' + k]) # cast to a 1 dimension thing
                    dataset["dec_" + k] = 10 - pd.DataFrame(pd.qcut(prob_plus_smallrandom, 10, labels = False), index = self.feature_data[j].index)
                    # append the different datasets
                data_set = data_set.append(dataset)
            final = final.append(data_set)
        return final
    
    def aggregate_over_deciles(self):
        """ Create eval_t_tot
        
        This function builds the pandas dataframe eval_t_tot and contains the aggregated output.
        The data is aggregated over datasets (feature and label-data pairs) and list of models.
        
        Parameters
        ----------
        feature_data : list of objects
            Objects containing the X matrix for one or more different datasets.
            
        label_data : list of objects 
            Objects of the y vector for one or more different datasets.
            
        dataset_labels : list of str 
            Containing the names of the different feature `feature_data` and label `label_data` data combination pairs.
        
        models : list of objects
            Containing the sk-learn model objects
        
        model_labels : list of str
            Names of the (sk-learn) models
            
        seed : int, default 999
            Make results reproducible, in the case of a small dataset the data cannot be split into 10 unique deciles.

        Returns
        -------
        Pandas dataframe for all dataset and model combination for deciles 1 tot 10.
        It already contains almost all necessary information for model plotting.

        Raises
        ------
        ValueError: If there is no match with the complete list or the input list again.
        """
        scores_and_deciles = self.prepare_scores_and_deciles()
        scores_and_deciles['all'] = 1
        deciles_aggregate = pd.DataFrame()
        add_origin = pd.DataFrame()
        for i in range(len(self.model_labels)):
            for j in self.models[i].classes_:
                for k in self.dataset_labels:
                    add_origin_add = pd.DataFrame({
                        'model_label': self.model_labels[i], 'dataset_label': [k],  'target_class': [j], 'decile': [0], 
                        'tot': [0], 'pos': [0], 'neg': [0], 'pct': [0], 'postot': [0], 'negtot': [0], 
                        'tottot': [0], 'pcttot': [0], 'cumpos': [0], 'cumneg': [0], 'cumtot': [0], 'cumpct': [0], 
                        'gain': [0], 'cumgain': [0], 'gain_ref': [0], 'pct_ref': [0], 'gain_opt': [0], 
                        'lift': [0], 'cumlift': [0], 'cumlift_ref': [1]
                    })
                    deciles_agg = []
                    deciles_agg = pd.DataFrame(index=range(1,11))
                    deciles_agg['model_label'] = self.model_labels[i]
                    deciles_agg['dataset_label'] = k
                    deciles_agg['target_class'] = j
                    deciles_agg['decile'] = range(1,11,1)
                    relvars = ['dec_%s' % j,'all']
                    deciles_agg['tot'] = scores_and_deciles[(scores_and_deciles.dataset_label == k) & (scores_and_deciles.model_label == self.model_labels[i])][relvars].groupby('dec_%s' % j).agg('sum')
                    scores_and_deciles['pos'] = scores_and_deciles.target_class == j
                    relvars = ['dec_%s' % j, 'pos']
                    deciles_agg['pos'] = scores_and_deciles[(scores_and_deciles.dataset_label == k) & (scores_and_deciles.model_label == self.model_labels[i])][relvars].groupby('dec_%s' % j).agg('sum')
                    scores_and_deciles['neg'] = scores_and_deciles.target_class != j
                    relvars = ['dec_%s' % j, 'neg']
                    deciles_agg['neg'] = scores_and_deciles[(scores_and_deciles.dataset_label == k) & (scores_and_deciles.model_label == self.model_labels[i])][relvars].groupby('dec_%s' % j).agg('sum')
                    deciles_agg['pct'] = deciles_agg.pos / deciles_agg.tot
                    deciles_agg['postot'] = deciles_agg.pos.sum()
                    deciles_agg['negtot'] = deciles_agg.neg.sum()
                    deciles_agg['tottot'] = deciles_agg.tot.sum()
                    deciles_agg['pcttot'] = deciles_agg.pct.sum()
                    deciles_agg['cumpos'] = deciles_agg.pos.cumsum()
                    deciles_agg['cumneg'] = deciles_agg.neg.cumsum()
                    deciles_agg['cumtot'] = deciles_agg.tot.cumsum()
                    deciles_agg['cumpct'] = deciles_agg.cumpos / deciles_agg.cumtot
                    deciles_agg['gain'] = deciles_agg.pos / deciles_agg.postot
                    deciles_agg['cumgain'] = deciles_agg.cumpos / deciles_agg.postot
                    deciles_agg['gain_ref'] = deciles_agg.decile / 10
                    deciles_agg['pct_ref'] = deciles_agg.postot / deciles_agg.tottot
                    deciles_agg['gain_opt'] = 1.0
                    deciles_agg.loc[(deciles_agg.cumtot / deciles_agg.postot) <= 1.0, 'gain_opt'] = (deciles_agg.cumtot / deciles_agg.postot)
                    deciles_agg['lift'] = deciles_agg.pct / (deciles_agg.postot / deciles_agg.tottot)
                    deciles_agg['cumlift'] = deciles_agg.cumpct / (deciles_agg.postot / deciles_agg.tottot)
                    deciles_agg['cumlift_ref'] = 1

                    deciles_aggregate = deciles_aggregate.append(deciles_agg, ignore_index = True)
                    add_origin = pd.concat([add_origin, add_origin_add], axis = 0)

        deciles_aggregate = pd.concat([add_origin, deciles_aggregate], axis = 0).sort_values(by=['model_label', 'dataset_label', 'target_class', 'decile'])
        cols = deciles_aggregate.columns
        return deciles_aggregate[cols]
    
    def plotting_scope(self, scope = 'no_comparison', select_model_label = [], select_dataset_label = [], select_targetclass = [], select_smallest_targetclass = True):
        """ Create plot_input
        
        This function builds the pandas dataframe plot_input wich is a subset of scores_and_deciles.
        The dataset is the subset of scores_and_deciles that is dependent of 1 of the 4 evaluation types that a user can request.
        
        How is this function evaluated?
        There are 4 different perspectives to evaluate model plots.
        1. no_comparison
        This perspective will show a single plot that contains the viewpoint from:
        1 dataset
        1 model
        1 target class
        
        2. compare_models 
        This perspective will show plots that contains the viewpoint from:
        2 or more different models
        1 dataset
        1 target class
        
        3. compare_datasets
        This perspective will show plots that contains the viewpoint from:
        2 or more different datasets
        1 model
        1 target class
        
        4. compare_datasets
        This perspective will show plots that contains the viewpoint from:
        2 or more different target classes
        1 dataset
        1 model
        
        Parameters
        ----------
        scope : str, default is 'no_comparison'
            One of the 4 evaluation types: 'no_comparison', 'compare_models', 'compare_datasets', 'compare_datasets' or 'compare_targetclasses'.
        
        select_model_label : list of str
            List of one or more elements from the model_name parameter.
        
        select_dataset_label : list of str
            List of one or more elements from the description parameter.
        
        select_targetclass : list of str
            List of one or more elements from the label data.
        
        select_smallest_targetclass : bool, default = True
            Should the plot only contain the results of the smallest targetclass.
            If True, the specific target is defined from the first dataset.

        Returns
        -------
        Pandas dataframe, a subset of scores_and_deciles, for all dataset, model and target value combinations for deciles 1 tot 10.
        It contains all necessary information for model plotting.

        Raises
        ------
        ValueError: If the wrong `scope` value is specified.
        """
        deciles_aggregate = self.aggregate_over_deciles()
        deciles_aggregate['scope'] = scope

        if scope not in ('no_comparison', 'compare_models', 'compare_datasets', 'compare_targetclasses'):
            raise ValueError('Invalid scope value, it must be one of the following: no_comparison, compare_models, compare_datasets or compare_targetclasses.')
        
        # check parameters
        select_model_label = check_input(select_model_label, self.model_labels, 'select_model_label')
        select_dataset_label = check_input(select_dataset_label, self.dataset_labels, 'select_dataset_label')
        select_targetclass = check_input(select_targetclass, list(self.models[1].classes_), 'select_targetclass')

        if scope == 'no_comparison':
            print('No comparison specified! Single evaluation line will be plotted')
            if len(select_model_label) >= 1:
                select_model_label = select_model_label
            else:
                select_model_label = self.model_labels
            if len(select_dataset_label) >= 1:
                select_dataset_label = select_dataset_label
            else:
                select_dataset_label = self.dataset_labels
            if len(select_targetclass) >= 1:
                select_targetclass = select_targetclass
            elif select_smallest_targetclass == True:
                select_targetclass = [self.label_data[0].value_counts(ascending = True).idxmin()]
                print("The label with smallest class is %s" % select_targetclass)
            else:
                select_targetvalue = list(self.models[1].classes_)
            plot_input = deciles_aggregate[
                (deciles_aggregate.model_label == select_model_label[0]) & 
                (deciles_aggregate.dataset_label == select_dataset_label[0]) & 
                (deciles_aggregate.target_class == select_targetclass[0])]
            print('Target value %s plotted for dataset %s and model %s.' % (select_targetclass[0], select_dataset_label[0], select_model_label[0]))
        elif scope == 'compare_models':
            print('compare models')
            if len(select_model_label) >= 2:
                select_model_label = select_model_label
            else:
                select_model_label = self.model_labels
            if len(select_dataset_label) >= 1:
                select_dataset_label = select_dataset_label
            else:
                select_dataset_label = self.dataset_labels
            if len(select_targetclass) >= 1:
                select_targetclass = select_targetclass
            elif select_smallest_targetclass == True:
                select_targetclass = [self.label_data[0].value_counts(ascending = True).idxmin()]
                print("The label with smallest class is %s" % select_targetclass)
            else:
                select_targetclass = list(self.models[1].classes_)
            plot_input = deciles_aggregate[
                (deciles_aggregate.model_label.isin(select_model_label)) &
                (deciles_aggregate.dataset_label == select_dataset_label[0]) &
                (deciles_aggregate.target_class == select_targetclass[0])]
        elif scope == 'compare_datasets':
            print('compare datasets')
            if len(select_model_label) >= 1:
                select_model_label = select_model_label
            else:
                select_model_label = self.model_labels
            if len(select_dataset_label) >= 2:
                select_dataset_label = select_dataset_label
            else:
                select_dataset_label = self.dataset_labels
            if len(select_targetclass) >= 1:
                select_targetclass = select_targetclass
            elif select_smallest_targetclass == True:
                select_targetclass = [self.label_data[0].value_counts(ascending = True).idxmin()]
                print("The label with smallest class is %s" % select_targetclass)
            else:
                select_targetclass = list(self.models[1].classes_)
            plot_input = deciles_aggregate[
                (deciles_aggregate.model_label == select_model_label[0]) &
                (deciles_aggregate.dataset_label.isin(select_dataset_label)) &
                (deciles_aggregate.target_class == select_targetclass[0])]
        else: # scope == 'compare_targetclasses'
            print('compare target values')
            if len(select_model_label) >= 1:
                select_model_label = select_model_label
            else:
                select_model_label = self.model_labels
            if len(select_dataset_label) >= 1:
                select_dataset_label = select_dataset_label
            else:
                select_dataset_label = self.dataset_labels
            if len(select_targetclass) >= 2:
                select_targetclass = select_targetclass
            else:
                select_targetclass = list(self.models[1].classes_)
            plot_input = deciles_aggregate[
                (deciles_aggregate.model_label == select_model_label[0]) &
                (deciles_aggregate.dataset_label == select_dataset_label[0]) &
                (deciles_aggregate.target_class.isin(select_targetclass))]
        return plot_input
