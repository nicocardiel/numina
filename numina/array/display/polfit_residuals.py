#
# Copyright 2015-2016 Universidad Complutense de Madrid
#
# This file is part of Numina
#
# Numina is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Numina is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Numina.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import division
from __future__ import print_function

import argparse
import numpy as np
from numpy.polynomial import Polynomial

from ..display.pause_debugplot import pause_debugplot


def polfit_residuals(
        x, y, deg, reject=None,
        color='b', size=75,
        xlim=None, ylim=None,
        xlabel=None, ylabel=None, title=None,
        use_r=False,
        debugplot=0):
    """Polynomial fit with display of residuals and additional work with R.

    Parameters
    ----------
    x : 1d numpy array, float
        X coordinates of the data being fitted.
    y : 1d numpy array, float
        Y coordinates of the data being fitted.
    deg : int
        Degree of the fitting polynomial.
    reject : None or 1d numpy array (bool)
        If not None, it must be a boolean array indicating whether a
        particular point is rejected or not (i.e., the rejected points
        are flagged as True in this array). Rejected points are
        displayed but not used in the fit.
    color : single character or 1d numpy array of characters
        Color for all the symbols (single character) or for each
        individual symbol (array of color names with the same length as
        'x' or 'y'). If 'color' is a single character, the rejected
        points are displayed in red color, whereas when 'color' is an
        array of color names, rejected points are displayed with the
        color provided in this array.
    size : int
        Marker size for all the symbols (single character) or for each
        individual symbol (array of integers with the same length as
        'x' or 'y').
    xlim : tuple (floats)
        Plot limits in the X axis.
    ylim : tuple (floats)
        Plot limits in the Y axis.
    xlabel : string
        Character string for label in X axis.
    ylabel : string
        Character string for label in y axis.
    title : string
        Character string for graph title.
    use_r : bool
        If True, the function computes several fits, using R, to
        polynomials of degree deg, deg+1 and deg+2 (when possible).
    debugplot : int
        Determines whether intermediate computations and/or plots
        are displayed:
        00 : no debug, no plots
        01 : no debug, plots without pauses
        02 : no debug, plots with pauses
        10 : debug, no plots
        11 : debug, plots without pauses
        12 : debug, plots with pauses

    Return
    ------
    poly : instance of Polynomial (numpy)
        Result from the polynomial fit using numpy Polynomial. Only
        points not flagged as rejected are employed in the fit.
    yres : 1d numpy array, float
        Residuals from polynomial fit. Note that the residuals are
        computed for all the points, including the rejected ones. In
        this way the dimension of this array is the same as the
        dimensions of the input 'x' and 'y' arrays.

    """

    # protections
    if type(x) is not np.ndarray:
        raise ValueError("x=" + str(x) + " must be a numpy.ndarray")
    elif x.ndim != 1:
        raise ValueError("x.ndim=" + str(x.ndim) + " must be 1")
    if type(y) is not np.ndarray:
        raise ValueError("y=" + str(y) + " must be a numpy.ndarray")
    elif y.ndim != 1:
        raise ValueError("y.ndim=" + str(y.ndim) + " must be 1")
    npoints = x.size
    if npoints != y.size:
        raise ValueError("x.size != y.size")
    if reject is not None:
        if npoints != reject.size:
            raise ValueError("x.size != reject.size")
    if type(deg) not in [np.int, np.int64]:
        raise ValueError("deg=" + str(deg) +
                         " is not a valid integer")

    # select points for fit
    if reject is None:
        xfitted = np.copy(x)
        yfitted = np.copy(y)
        xrejected = None
        yrejected = None
        nfitted = npoints
        nrejected = 0
    else:
        xfitted = x[np.logical_not(reject)]
        yfitted = y[np.logical_not(reject)]
        xrejected = x[reject]
        yrejected = y[reject]
        # update number of points for fit
        nfitted = xfitted.size
        nrejected = sum(reject)

    if deg > nfitted - 1:
        raise ValueError("Insufficient nfitted=" + str(nfitted) +
                         " for deg=" + str(deg))

    # polynomial fits using R
    if use_r:
        from ..rutilities import LinearModelYvsX
        print("\n>>> Total number of points:", nfitted)
        # using orthogonal polynomials
        for delta_deg in [2, 1, 0]:
            deg_eff = deg + delta_deg
            if deg_eff <= nfitted - 1:
                myfit = LinearModelYvsX(x=xfitted, y=yfitted, degree=deg_eff,
                                        raw=False)
                print(">>> Fit with R, using orthogonal polynomials:")
                print(myfit.summary)
                pause_debugplot(debugplot)
        # fit using raw polynomials
        myfit = LinearModelYvsX(x=xfitted, y=yfitted, degree=deg, raw=True)
        print(">>> Fit with R, using raw polynomials:")
        print(myfit.summary)
        pause_debugplot(debugplot)

    # fit with requested degree (and raw polynomials)
    poly = Polynomial.fit(x=xfitted, y=yfitted, deg=deg)
    poly = Polynomial.cast(poly)

    # compute residuals
    yres = y - poly(x)  # of all the points
    yres_fitted = yfitted - poly(xfitted)  # points employed in the fit
    yres_rejected = None
    if nrejected > 0:
        yres_rejected = yrejected - poly(xrejected)  # points rejected

    if debugplot >= 10:
        print(">>> Polynomial fit:\n", poly)

    if debugplot % 10 != 0:
        # define colors, markers and sizes for symbols
        if np.array(color).size == 1:
            mycolor = np.array([color] * npoints)
            if reject is not None:
                mycolor[reject] = 'r'
        elif np.array(color).size == npoints:
            mycolor = np.copy(np.array(color))
        elif np.array(color).shape[0] == npoints:  # assume rgb color
            mycolor = np.copy(np.array(color))
        else:
            raise ValueError("color=" + str(color) +
                             " doesn't have the expected dimension")
        if np.array(size).size == 1:
            mysize = np.repeat([size], npoints)
        elif np.array(size).size == npoints:
            mysize = np.copy(np.array(size))
        else:
            raise ValueError("size=" + str(size) +
                             " doesn't have the expected dimension")

        if reject is None:
            cfitted = np.copy(mycolor)
            crejected = None
            sfitted = np.copy(mysize)
            srejected = None
        else:
            cfitted = mycolor[np.logical_not(reject)]
            crejected = mycolor[reject]
            sfitted = mysize[np.logical_not(reject)]
            srejected = mysize[reject]

        import matplotlib
        matplotlib.use('Qt4Agg')
        import matplotlib.pyplot as plt
        fig = plt.figure()

        # residuals
        ax2 = fig.add_subplot(2, 1, 2)
        if xlabel is None:
            ax2.set_xlabel('x')
        else:
            ax2.set_xlabel(xlabel)
        ax2.set_ylabel('residuals')
        if xlim is None:
            xmin = min(x)
            xmax = max(x)
            dx = xmax - xmin
            xmin -= dx/20
            xmax += dx/20
        else:
            xmin, xmax = xlim
        ax2.set_xlim([xmin, xmax])
        ymin = min(yres_fitted)
        ymax = max(yres_fitted)
        dy = ymax - ymin
        ymin -= dy/20
        ymax += dy/20
        ax2.set_ylim([ymin, ymax])
        ax2.axhline(y=0.0, color="black", linestyle="dashed")
        ax2.scatter(xfitted, yres_fitted, color=cfitted,
                    marker='o',
                    edgecolor='k', s=sfitted)
        if nrejected > 0:
            ax2.scatter(xrejected, yres_rejected,
                        marker='x', s=srejected,
                        color=crejected)

        # original data and polynomial fit
        ax = fig.add_subplot(2, 1, 1, sharex=ax2)
        if ylabel is None:
            ax.set_ylabel('y')
        else:
            ax.set_ylabel(ylabel)
        ax.set_xlim([xmin, xmax])
        if ylim is None:
            ymin = min(y)
            ymax = max(y)
            dy = ymax - ymin
            ymin -= dy/20
            ymax += dy/20
        else:
            ymin, ymax = ylim
        ax.set_ylim([ymin, ymax])
        ax.scatter(xfitted, yfitted,
                   color=cfitted, marker='o', edgecolor='k',
                   s=sfitted, label="fitted data")
        xpol = np.linspace(start=xmin, stop=xmax, num=1000)
        ypol = poly(xpol)
        ax.plot(xpol, ypol, 'c-', label="fit")
        if nrejected > 0:
            ax.scatter(xrejected, yrejected,
                       marker='x', s=srejected, color=crejected,
                       label="rejected")

        # shrink axes and put a legend
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0,
                          box.width, box.height * 0.92])
        delta_ybox = box.height*0.15
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 - delta_ybox,
                         box.width, box.height * 0.92])
        ax.legend(loc=3, bbox_to_anchor=(0.0, 1.1, 1., 0.07),
                  mode="expand", borderaxespad=0., ncol=4,
                  numpoints=1)

        # graph title
        if title is not None:
            plt.title(title + "\n\n")

        plt.show(block=False)
        plt.pause(0.001)
        pause_debugplot(debugplot)

    # return result
    return poly, yres


def polfit_residuals_with_sigma_rejection(
        x, y, deg, times_sigma_reject,
        color='b', size=75,
        xlim=None, ylim=None,
        xlabel=None, ylabel=None, title=None,
        use_r=None,
        debugplot=0):
    """Polynomial fit with iterative rejection of points.

    This function makes use of function polfit_residuals for display
    purposes.

    Parameters
    ----------
    x : 1d numpy array, float
        X coordinates of the data being fitted.
    y : 1d numpy array, float
        Y coordinates of the data being fitted.
    deg : int
        Degree of the fitting polynomial.
    times_sigma_reject : float
        Number of times the standard deviation to reject points
        iteratively. If None, the fit does not reject any point.
    color : single character or 1d numpy array of characters
        Color for all the symbols (single character) or for each
        individual symbol (array of color names with the same length as
        'x' or 'y'). If 'color' is a single character, the rejected
        points are displayed in red color, whereas when 'color' is an
        array of color names, rejected points are displayed with the
        color provided in this array.
    size : int
        Marker size for all the symbols (single character) or for each
        individual symbol (array of integers with the same length as
        'x' or 'y').
    xlim : tuple (floats)
        Plot limits in the X axis.
    ylim : tuple (floats)
        Plot limits in the Y axis.
    xlabel : string
        Character string for label in X axis.
    ylabel : string
        Character string for label in y axis.
    title : string
        Character string for graph title.
    use_r : bool
        If True, the function computes several fits, using R, to
        polynomials of degree deg, deg+1 and deg+2 (when possible).
    debugplot : int
        Determines whether intermediate computations and/or plots
        are displayed:
        00 : no debug, no plots
        01 : no debug, plots without pauses
        02 : no debug, plots with pauses
        10 : debug, no plots
        11 : debug, plots without pauses
        12 : debug, plots with pauses

    Return
    ------
    poly : instance of Polynomial (numpy)
        Result from the polynomial fit using numpy Polynomial. Only
        points not flagged as rejected are employed in the fit.
    yres : 1d numpy array, float
        Residuals from polynomial fit. Note that the residuals are
        computed for all the points, including the rejected ones. In
        this way the dimension of this array is the same as the
        dimensions of the input 'x' and 'y' arrays.
    reject : 1d numpy array, bool
        Boolean array indicating rejected points.

    """

    # protections
    if type(x) is not np.ndarray:
        raise ValueError("x=" + str(x) + " must be a numpy.ndarray")
    elif x.ndim != 1:
        raise ValueError("x.ndim=" + str(x.ndim) + " must be 1")
    if type(y) is not np.ndarray:
        raise ValueError("y=" + str(y) + " must be a numpy.ndarray")
    elif y.ndim != 1:
        raise ValueError("y.ndim=" + str(y.ndim) + " must be 1")
    npoints = x.size
    if npoints != y.size:
        raise ValueError("x.size != y.size")
    if type(deg) not in [np.int, np.int64]:
        raise ValueError("deg=" + str(deg) +
                         " is not a valid integer")
    if deg >= npoints:
        raise ValueError("Polynomial degree=" + str(deg) +
                         " can't be fitted with npoints=" + str(npoints))

    # initialize boolean rejection array
    reject = np.zeros(npoints, dtype=np.bool)

    # if there is no room to remove any point, compute a fit without
    # rejection
    if deg == npoints - 1:
        poly, yres = polfit_residuals(x=x, y=y, deg=deg, reject=None,
                                      color=color, size=size,
                                      xlim=xlim, ylim=ylim,
                                      xlabel=xlabel, ylabel=ylabel,
                                      title=title,
                                      use_r=use_r,
                                      debugplot=debugplot)
        return poly, yres, reject

    # main loop to reject points iteratively
    loop_to_reject_points = True
    poly = None
    yres = None
    while loop_to_reject_points:
        poly, yres = polfit_residuals(x=x, y=y, deg=deg, reject=reject,
                                      color=color, size=size,
                                      xlim=xlim, ylim=ylim,
                                      xlabel=xlabel, ylabel=ylabel,
                                      title=title,
                                      use_r=use_r,
                                      debugplot=debugplot)
        # check that there is room to remove a point with the current
        # polynomial degree
        npoints_effective = npoints - np.sum(reject)
        if deg < npoints_effective - 1:
            # determine robuts standard deviation, excluding points
            # already rejected
            # --- method 1 ---
            # yres_fitted = yres[np.logical_not(reject)]
            # q25, q75 = np.percentile(yres_fitted, q=[25.0, 75.0])
            # rms = 0.7413 * (q75 - q25)
            # --- method 2 ---
            yres_fitted = np.abs(yres[np.logical_not(reject)])
            rms = np.median(yres_fitted)
            if debugplot >= 10:
                print("--> robust rms:", rms)
            # reject fitted point exceeding the threshold with the
            # largest deviation (note: with this method only one point
            # is removed in each iteration of the loop; this allows the
            # recomputation of the polynomial fit which, sometimes,
            # transforms deviant points into good ones)
            index_to_remove = []
            for i in range(npoints):
                if not reject[i]:
                    if np.abs(yres[i]) > times_sigma_reject * rms:
                        index_to_remove.append(i)
                        if debugplot >= 10:
                            print('--> suspicious point #', i + 1)
            if len(index_to_remove) == 0:
                if debugplot >= 10:
                    print('==> no need to remove any point')
                loop_to_reject_points = False
            else:
                imax = np.argmax(np.abs(yres[index_to_remove]))
                reject[index_to_remove[imax]] = True
                if debugplot >= 10:
                    print('==> removing point #', index_to_remove[imax] + 1)
        else:
            loop_to_reject_points = False

    # return result
    return poly, yres, reject


def polfit_residuals_with_cook_rejection(
        x, y, deg, times_sigma_cook,
        color='b', size=75,
        xlim=None, ylim=None,
        xlabel=None, ylabel=None, title=None,
        use_r=None,
        debugplot=0):
    """Polynomial fit with iterative rejection of points.

    This function makes use of function polfit_residuals for display
    purposes.

    Parameters
    ----------
    x : 1d numpy array, float
        X coordinates of the data being fitted.
    y : 1d numpy array, float
        Y coordinates of the data being fitted.
    deg : int
        Degree of the fitting polynomial.
    times_sigma_cook : float
        Number of times the standard deviation of Cook's distances
        above the median value to reject points iteratively.
    color : single character or 1d numpy array of characters
        Color for all the symbols (single character) or for each
        individual symbol (array of color names with the same length as
        'x' or 'y'). If 'color' is a single character, the rejected
        points are displayed in red color, whereas when 'color' is an
        array of color names, rejected points are displayed with the
        color provided in this array.
    size : int
        Marker size for all the symbols (single character) or for each
        individual symbol (array of integers with the same length as
        'x' or 'y').
    xlim : tuple (floats)
        Plot limits in the X axis.
    ylim : tuple (floats)
        Plot limits in the Y axis.
    xlabel : string
        Character string for label in X axis.
    ylabel : string
        Character string for label in y axis.
    title : string
        Character string for graph title.
    use_r : bool
        If True, the function computes several fits, using R, to
        polynomials of degree deg, deg+1 and deg+2 (when possible).
    debugplot : int
        Determines whether intermediate computations and/or plots
        are displayed:
        00 : no debug, no plots
        01 : no debug, plots without pauses
        02 : no debug, plots with pauses
        10 : debug, no plots
        11 : debug, plots without pauses
        12 : debug, plots with pauses

    Return
    ------
    poly : instance of Polynomial (numpy)
        Result from the polynomial fit using numpy Polynomial. Only
        points not flagged as rejected are employed in the fit.
    yres : 1d numpy array, float
        Residuals from polynomial fit. Note that the residuals are
        computed for all the points, including the rejected ones. In
        this way the dimension of this array is the same as the
        dimensions of the input 'x' and 'y' arrays.
    reject : 1d numpy array, bool
        Boolean array indicating rejected points.

    """

    # protections
    if type(x) is not np.ndarray:
        raise ValueError("x=" + str(x) + " must be a numpy.ndarray")
    elif x.ndim != 1:
        raise ValueError("x.ndim=" + str(x.ndim) + " must be 1")
    if type(y) is not np.ndarray:
        raise ValueError("y=" + str(y) + " must be a numpy.ndarray")
    elif y.ndim != 1:
        raise ValueError("y.ndim=" + str(y.ndim) + " must be 1")
    npoints = x.size
    if npoints != y.size:
        raise ValueError("x.size != y.size")
    if type(deg) not in [np.int, np.int64]:
        raise ValueError("deg=" + str(deg) +
                         " is not a valid integer")
    if deg >= npoints:
        raise ValueError("Polynomial degree=" + str(deg) +
                         " can't be fitted with npoints=" + str(npoints))

    # initialize boolean rejection array
    reject = np.zeros(npoints, dtype=np.bool)

    # if there is no room to remove two points, compute a fit without
    # rejection
    if deg == npoints - 1 or deg == npoints - 2:
        poly, yres = polfit_residuals(x=x, y=y, deg=deg, reject=None,
                                      color=color, size=size,
                                      xlim=xlim, ylim=ylim,
                                      xlabel=xlabel, ylabel=ylabel,
                                      title=title,
                                      use_r=use_r,
                                      debugplot=debugplot)
        return poly, yres, reject

    # main loop to reject points iteratively
    loop_to_reject_points = True
    poly = None
    yres = None
    any_point_removed = False
    while loop_to_reject_points:
        # fit to compute residual variance (neglecting already
        # rejected points)
        poly, yres = polfit_residuals(x=x, y=y, deg=deg, reject=reject,
                                      color=color, size=size,
                                      xlim=xlim, ylim=ylim,
                                      xlabel=xlabel, ylabel=ylabel,
                                      title=title,
                                      use_r=use_r,
                                      debugplot=debugplot)
        npoints_effective = npoints - np.sum(reject)
        residual_variance = np.sum(yres*yres)/float(npoints_effective-deg-1)
        # check that there is room to remove two points with the
        # current polynomial degree
        if deg <= npoints_effective - 2:
            cook_distance = np.zeros(npoints)
            for i in range(npoints):
                if not reject[i]:
                    reject_cook = np.copy(reject)
                    reject_cook[i] = True
                    poly_cook, yres_cook = polfit_residuals(
                        x=x, y=y, deg=deg, reject=reject_cook,
                        color=color, size=size,
                        xlim=xlim, ylim=ylim,
                        xlabel=xlabel, ylabel=ylabel,
                        title="Computing Cook's distance for point " +
                              str(i+1),
                        use_r=False,
                        debugplot=0)
                    yres_cook_fitted = yres_cook[np.logical_not(reject)]
                    cook_distance[i] = \
                        np.sum(yres_cook_fitted*yres_cook_fitted) / \
                        (2*residual_variance)
                else:
                    cook_distance[i] = np.inf
                if debugplot >= 10:
                    print('i, cook_distance[i]:', i, cook_distance[i])
            # determine median absolute cook distance, excluding points
            # already rejected
            dist_cook_fitted = np.abs(cook_distance[np.logical_not(reject)])
            q50 = np.median(dist_cook_fitted)
            # rms computed from the previous data after removing the
            # point with the largest deviation
            rms = np.std(np.sort(dist_cook_fitted)[:-2])
            if debugplot >= 10:
                print("--> median.......:", q50)
                print("--> rms -2 points:", rms)
            # reject fitted point exceeding the threshold with the
            # largest Cook distance (note: with this method only one
            # point is removed in each iteration of the loop). If the
            # polynomial degree is larger than 1, only intermediate
            # points can be discarded (i.e., the first and last point
            # are never rejected because the curvature of the
            # extrapolated polynomials leads to false outliers)
            index_to_remove = []
            if deg > 1:
                n1 = 1
                n2 = npoints - 1
            else:
                n1 = 0
                n2 = npoints
            for i in range(n1, n2):
                if not reject[i]:
                    if np.abs(cook_distance[i]-q50) > times_sigma_cook * rms:
                        index_to_remove.append(i)
                        if debugplot >= 10:
                            print('--> suspicious point #', i + 1)
            if len(index_to_remove) == 0:
                if debugplot >= 10:
                    if any_point_removed:
                        print('==> no need to remove any additional point')
                    else:
                        print('==> no need to remove any point')
                loop_to_reject_points = False
            else:
                imax = np.argmax(np.abs(cook_distance[index_to_remove]))
                reject[index_to_remove[imax]] = True
                any_point_removed = True
                if debugplot >= 10:
                    print('==> removing point #', index_to_remove[imax] + 1)
        else:
            loop_to_reject_points = False

    # return result
    return poly, yres, reject


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(prog='polfit_residuals')
    parser.add_argument("filename",
                        help="ASCII file with data in columns")
    parser.add_argument("cols",
                        help="tuple col1,col2")
    parser.add_argument("polydeg",
                        help="polynomial degree")
    parser.add_argument("--times_sigma_reject",
                        help="Times sigma to reject points" +
                             " (default=None)",
                        default=None)
    parser.add_argument("--times_sigma_cook",
                        help="Times sigma to reject points" +
                             " (default=None)",
                        default=None)
    args = parser.parse_args(args)

    # ASCII file
    filename = args.filename

    # columns to be plotted (first column will be number 1 and not 0)
    tmp_str = args.cols.split(",")
    col1, col2 = int(tmp_str[0]), int(tmp_str[1])
    col1 -= 1
    col2 -= 1

    # polynomial degree
    polydeg = int(args.polydeg)

    # times_sigma_reject
    if args.times_sigma_reject is None:
        times_sigma_reject = None
    else:
        times_sigma_reject = float(args.times_sigma_reject)

    # times_sigma_cook
    if args.times_sigma_cook is None:
        times_sigma_cook = None
    else:
        times_sigma_cook = float(args.times_sigma_cook)

    # check
    if times_sigma_reject is not None and times_sigma_cook is not None:
        raise ValueError("ERROR: times_sigma_reject and times_sigma_cook" +
                         " cannot be employed simultaneously")

    # read ASCII file
    bigtable = np.genfromtxt(filename)
    x = bigtable[:, col1]
    y = bigtable[:, col2]

    # plot fit and residuals
    if times_sigma_reject is None and times_sigma_cook is None:
        polfit_residuals(x, y, polydeg, debugplot=12)
    elif times_sigma_reject is not None:
        polfit_residuals_with_sigma_rejection(
            x, y, polydeg, times_sigma_reject, debugplot=12
        )
    elif times_sigma_cook is not None:
        polfit_residuals_with_cook_rejection(
            x, y, polydeg, times_sigma_cook, debugplot=12
        )


if __name__ == '__main__':
    main()
