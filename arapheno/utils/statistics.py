import logging
import scipy as sp
from scipy import stats

logger = logging.getLogger(__name__)

SUPPORTED_TRANSFORMATIONS = ("no","log", "sqrt", "sqr", "arcsin_sqrt", "box_cox","ascombe")

def transform(values, transformation, standard=True):
    if transformation == 'no':
        return sp.array(values)
    if transformation == 'sqrt':
        return _sqrt_transform(values, standard=standard)
    elif transformation == 'ascombe':
        return _ascombe_transform(values)
    elif transformation == 'log':
        return _log_transform(values, standard=standard)
    elif transformation == 'sqr':
        return _sqr_transform(values, standard=standard)
    elif transformation == 'exp':
        return _exp_transform(values, standard=standard)
    elif transformation == 'arcsin_sqrt':
        return _arcsin_sqrt_transform(values)
    elif transformation == 'box_cox':
        return _box_cox_transform(values, standard=standard)
    else:
        raise Exception('Transformation %s unknown' % transformation)

def _sqrt_transform(values, standard=True):
    a = sp.array(values)
    if standard:
        vals = sp.sqrt((a - min(a)) + 0.1 * sp.var(a))
    else:
        vals = sp.sqrt(a)
    return vals

def _log_transform(values, standard=True):
    a = sp.array(values)
    if standard:
        vals = sp.log((a - min(a)) + 0.1 * sp.var(a))
    else:
        vals = sp.log(a)
    return vals

def _ascombe_transform(values):
    a = sp.array(values)
    vals = 2.0 * sp.sqrt(a + 3.0 / 8.0)
    return vals


def _sqr_transform(values,  standard=True):
    a = sp.array(values)
    if standard:
        vals = ((a - min(a)) + 0.1 * sp.var(a)) * ((a - min(a)) + 0.1 * sp.var(a))
    else:
        vals = a * a
    return vals

def _exp_transform(values, standard=True):
    a = sp.array(values)
    if standard:
        vals = sp.exp((a - min(a)) + 0.1 * sp.var(a))
    else:
        vals = sp.exp(a)
    return vals

def _arcsin_sqrt_transform(values):
    a = sp.array(values)
    if min(a) < 0 or max(a) > 1:
        logger.debug('Some values are outside of range [0,1], hence skipping transformation!')
        return None
    else:
        vals = sp.arcsin(sp.sqrt(a))
    return vals

def _box_cox_transform(values, standard=True):
    """
    Performs the Box-Cox transformation, over different ranges, picking the optimal one w. respect to normality.
    """
    a = sp.array(values)
    if standard:
        vals = (a - min(a)) + 0.1 * sp.var(a)
    else:
        vals = a
    sw_pvals = []
    lambdas = sp.arange(-2.0, 2.1, 0.1)
    for l in lambdas:
        if l == 0:
            vs = sp.log(vals)
        else:
            vs = ((vals ** l) - 1) / l
        r = stats.shapiro(vs)
        if sp.isfinite(r[0]):
            pval = r[1]
        else:
            pval = 0.0
        sw_pvals.append(pval)
    i = sp.argmax(sw_pvals)
    l = lambdas[i]
    if l == 0:
        vs = sp.log(vals)
    else:
        vs = ((vals ** l) - 1) / l
    return vs

def calculate_sp_pval(values):
    r = stats.shapiro(values)
    if sp.isfinite(r[0]):
        sp_pval = r[1]
    else:
        sp_pval = 0.0
    return sp_pval


