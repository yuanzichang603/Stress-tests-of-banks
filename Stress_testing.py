import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.tsa.stattools import adfuller


def forward_selected(data, response):
    remaining = set(data.columns)
    remaining.remove(response)
    selected = []
    current_score, best_new_score = 0.0, 0.0
    while remaining and current_score == best_new_score:
        scores_with_candidates = []
        for candidate in remaining:
            formula = "{} ~ {} + 1".format(response,
                                           ' + '.join(selected + [candidate]))
            model = smf.ols(formula, data).fit()
            score = model.rsquared_adj
            pvalues = model.pvalues[candidate]
            scores_with_candidates.append((score, candidate, pvalues))
        scores_with_candidates.sort()
        best_new_score, best_candidate, the_pvalues = scores_with_candidates.pop()
        if current_score < best_new_score and the_pvalues <= 0.05:
            remaining.remove(best_candidate)
            selected.append(best_candidate)
            current_score = best_new_score
    formula = "{} ~ {} + 1".format(response,
                                   ' + '.join(selected))
    model = smf.ols(formula, data).fit()
    return model


def ADF_test(data, model):
    # start at [2:] to ignore intercept and y[-1] vaiable
    for i in model.params.keys()[2:]:
        temp = data[i]
        result = adfuller(temp, maxlag=9, regression='c', autolag='AIC')
        if result[0] <= result[4]['5%']:
            print('For', i, ': ')
            ADF_output(result, i)
        else:
            for j in range(1, 3):
                temp = temp.diff(j)[j:]
                result = adfuller(
                    temp, maxlag=9, regression='c', autolag='AIC')
                if result[0] <= result[4]['5%']:
                    print("For {variable}.diff({diff}): ".format(
                        variable=i, diff=j))
                    ADF_output(result, i)
                    # break the inner loop if the test pass
                    break
            else:
                # will be called if the previous loop did not end with a `break`
                print('For', i, ': ')
                print("{variable} fail the ADF test.".format(variable=i))


def Cointegration_test(model):
    resid = model.resid
    result = adfuller(resid, maxlag=9, regression='c', autolag='AIC')
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    for key, value in result[4].items():
        print('Critial Values:')
        print(f'   {key}, {value}')
    if result[1] <= 0.05:
        print('Reject the null hypothesis, resid does not have a unit root and pass the Cointegration test.')
    else:
        print("Resid have a unit root and fail the Cointegration test.")


def ADF_output(result, variable):
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    for key, value in result[4].items():
        print('Critial Values:')
        print(f'   {key}, {value}')
    print(
        'Reject the null hypothesis, variable {variable} does not have a unit root and pass the ADF test.'.format(variable=variable))
    print(' ')


def main():
    data = pd.read_excel('data.xls')

    print('1.Stepwise OLS follows: ')
    model = forward_selected(data, 'y')
    print('Model Output: ', model.model.formula)
    print(model.params)
    print('\n')

    print('2.ADF test follows: ')
    ADF_test(data, model)
    print('\n')

    print('3.Cointegration test follows：')
    Cointegration_test(model)


if __name__ == '__main__':
    main()
