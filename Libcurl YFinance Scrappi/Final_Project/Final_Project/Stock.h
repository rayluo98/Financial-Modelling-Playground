#include <cmath>
#include<vector>
#include<functional>
#include<queue>
#include<map>
#include<string>
using namespace std;
class Stock
{
private:
	// Stores ticker name of stock
	std::string ticker;
	// Stores ticker day 0 
	std::string day_zero;
	// Vector of Historical Performance for given stock
	std::vector<double> hist;
	// Vector of Historical dates for given stock
	std::vector<std::string> dates;
	// Vector of Historical returns for given stock
	std::vector<double> returns;
	// Keeps track of group number for stock [-1: undef, 0: low, 1: in-between, 2: high]
	int group;
	// Keeps surprise value of stock
	double surprise;
	// Stores Expected EPS value
	double exp_eps;
	// Stores Real EPS value
	double real_eps;
	// Boolean that tells whether stock has loaded data
	bool stored;
	// Last Price before Window [used for return calculation]
public:
	// Default Constructor
	Stock() {
		ticker = "";
		group = -1;
		surprise = -1;
		exp_eps = -1;
		real_eps = -1;
		day_zero = "";
		stored = false;
	}

	// Constructor of Stock object
	Stock(std::string ticker_, int group_, double exp_eps_, double real_eps_, double surprise_, std::string dayzero_) {
		ticker = ticker_;
		group = -1;
		surprise = surprise_;
		exp_eps = exp_eps_;
		real_eps = real_eps_;
		day_zero = dayzero_;
		stored = false;
	};

	// Retrieves name of stock
	std::string getName() {
		return ticker;
	}

	// set Group
	void setGroup(int grp) {
		group = grp;
	}

	// Retrieves real EPS
	double getEPSre() {
		return real_eps;
	}

	// Retrieves expected EPS
	double getEPSexp() {
		return exp_eps;
	}

	// returns group
	std::string getGroup() {
		if (group == -1) {
			return "Undefined";
		}
		else if (group == 0) {
			return "Low surprise group";
		}
		else if (group == 1) {
			return "In Between group";
		}
		else {
			return "High surprise group";
		}
	}

	// stored 
	void nowStored(bool check) {
		stored = check;
	}

	// check if it is stored

	bool checkStored() {
		return stored;
	}

	// Calculate Surprise
	void setSurprise() {
		//TO DO - calculate the surprise 
	}

	// Get Surprise 
	double getSurprise() {
		return surprise;
	}

	// Returns stock return
	std::vector<double> getReturns() {
		return returns;
	}

	// Returns vector of stock performance
	std::vector<double> getPerformance() {
		return hist;
	}

	// Add to stock history 
	void addData(double val, double ret, std::string date) {
		hist.push_back(val);
		dates.push_back(date);
		returns.push_back(ret);
	}

	// Resets stock history 
	void resetData() {
		hist.clear();
		dates.clear();
		returns.clear();
	}

	// Retrieves day for ith entry in our date vector
	std::string getDate(int i) {
		if (i >= 0 && i < dates.size()) {
			return dates[i];
		}
		else {
			exit(1);
		}
		return "";
	}

	// Returns day zero for stock
	std::string getDay() {
		return day_zero;
	}

};


