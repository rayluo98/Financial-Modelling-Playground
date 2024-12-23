import logging
import mip.conflict
import pandas as pd
## don't want to load these packages unless we need to
from mip import * 

class mipEngine(object):
    def __init__(self, sense = MAXIMIZE, solver_name = CBC):
        self._model = Model(sense, solver_name)

    def _optimize(self):
        self._model.max_gap = 0.05
        status = self._model.optimize(max_seconds=300)
        if status == OptimizationStatus.OPTIMAL:
            print('optimal solution cost {} found'.format(self._model.objective_value))
        elif status == OptimizationStatus.FEASIBLE:
            print('sol.cost {} found, best possible: {}'.format(self._model.objective_value, self._model.objective_bound))
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print('no feasible solution found, lower bound is: {}'.format(self._model.objective_bound))
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print('solution:')
            for v in self._model.vars:
                if abs(v.x) > 1e-6: # only printing non-zeros
                    print('{} : {}'.format(v.name, v.x))

    def _save(self, dir:str):
        self._model.write(dir)
        logging.Logger.info("Model saved to {0}".format(dir))
    
    def _load(self, dir:str):
        self._model.read(dir)
        logging.Logger.info("Model loaded from {0}".format(dir))
        logging.Logger.info('model has {} vars, {} constraints and {} nzs'
                            .format(self._model.num_cols, 
                                    self._model.num_rows, 
                                    self._model.num_nz))
        
    def _addVariables(self, var_names, var_bounds:list[tuple[float|None, float|None]] |None=None, var_type="None"):
        res_var = {}
        for index in range(len(var_names)):
            lb = var_bounds[0]
            ub = var_bounds[1]
            if ub == None:
                ub = float('inf')
            if lb == None:
                lb = -float('inf')
            if var_type == "Integer":
                mip_var_type = mip.INTEGER
            else:
                mip_var_type = mip.CONTINUOUS
            res_var[var_names[index]] = self._model.add_var(name = "x" + str(index),
                lb = lb, ub=ub, var_type=mip_var_type)
        return res_var 
            
    def _addConstraints(self, coeffs:pd.DataFrame, bounds:dict, 
                        var_bounds:list[tuple[float|None, float|None]] |None=None,
                        var_type: str = None):
        if coeffs.shape[0] != len(bounds):
            print("Bounds and Constraints Dimensions not the same!")
            return ## bounds and constraints not same size
        # adding variables into model 
        res_var = self._addVariables(coeffs.columns, (None, None), var_type)
        n = len(res_var)
        for feature, df_row in coeffs.iterrows():
            self._model.add_constr(xsum(res_var[ticker] * df_row[ticker] for ticker in res_var) ==
                                   bounds[feature], feature)
        ## need to add optimization function check

    def _addOptimization(self, coeffs:pd.DataFrame):
        self._model.objective()

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()