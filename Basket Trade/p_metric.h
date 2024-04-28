#pragma once

#include <vector>

namespace p_var_real {
	typedef std::vector<double> NumericVector;

	// Compute p-variation of vector x, raised to the power p
	// Assumption: size(x) < UINT_LEAST32_MAX
	double pvar(const NumericVector& x, double p);
}