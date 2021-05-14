#include <cmath>
#include<vector>
#include<functional>
#include<queue>
#include "Stock.h"
#include "libcurl.h"
#include<map>
#include <string>
#include <fstream>
#include <vector>
#include <stdio.h>
#include <iostream>
#include <utility> // std::pair
#include <stdexcept> // std::runtime_error
#include <sstream> // std::stringstream
#include <ctime>
#include <deque>
#include "curl.h"
#include "Threadpool.h"
#include <stdlib.h>
#include <time.h>
#include <math.h>
//#include "matrix.h"

using namespace std;



class comp {
public:
	// Comparator function
	bool operator()(Stock o1, Stock o2)
	{

		// There can be any condition
		// implemented as per the need
		// of the problem statement
		return (o1.getSurprise()
			> o2.getSurprise());
	}
};

double mean(double a[], int n)
{
	int sum = 0;
	for (int i = 0; i < n; i++)
		sum += a[i];
	return sum / n;
}

/*
double std(double* x, int len)
{
	double sum = 0;
	double average = mean(x, len);
	for (int i = 0; i < len; i++)
		sum += pow(x[i] - average, 2);
	return sqrt(sum / len);
}
*/


time_t dateToTimeT(int month, int day, int year) {
	// january 5, 2000 is passed as (1, 5, 2000)
	tm tmp = tm();
	tmp.tm_mday = day;
	tmp.tm_mon = month - 1;
	tmp.tm_year = year - 1900;
	return mktime(&tmp);
}

time_t stotime(std::string s) {
	// We convert our string into a time_t data type to allow easier time arithmetic
	struct tm t = { 0 };

	std::string delimiter = "-";
	int pos1 = s.find(delimiter);

	std::string day = s.substr(0, pos1); // token is "scott"
	s = s.substr(pos1 + 1, s.size());
	int pos2 = s.substr(0, s.size()).find(delimiter);
	std::string month = s.substr(0, pos2);
	std::string year = s.substr(pos2 + 1, s.size());
	// convert day to right format
	// convert month to right format
	if (month == "Jan"){
		month = "1";
	}
	else if (month == "Feb") {
		month = "2";
	}
	else if (month == "Mar") {
		month = "3";
	}
	else if (month == "May") {
		month = "5";
	}
	else if (month == "Aug") {
		month = "8";
	}
	else if (month == "Sep") {
		month = "9";
	}
	else if (month == "Oct") {
		month = "10";
	}
	else if (month == "Nov") {
		month = "11";
	}
	else if (month == "Dec") {
		month = "12";
	}

	// convert year to right format 
	year = "20" + year;
	return dateToTimeT(stoi(month), stoi(day), stoi(year));
}


std::string timetos(time_t t) {
	// We want to convert format 22-Oct-20 to 2020-08-22
	//cout << ctime(&t) << endl;

	// for testing we print out our new string
	std::string buffer = ctime(&t);

	return buffer;
}

class Interface
{
private:
	// STL Map of Stock - Key are Stock Tickers, Values are a map of Stock History
	std::map<std::string, Stock> stocks;
	// Priority Queue Storing the Keys of Stocks Ordered by Surprise Level
	priority_queue <Stock, std::vector<Stock>, comp> pq;
	// Matrix storing stats of different groups - Group 0 [low], Group 1 [in between], Group 2 [high]
	//matrix matrix_(3, 4);
	// Stores the IWB Price Data
	std::map < std::string, std::pair<double, double >> IWB;

	// The following stores for libcurl
	FILE* fp1; FILE* fp2;
	CURL* handle;
	CURLcode result;
	string sCookies, sCrumb;
	const char outfilename[FILENAME_MAX] = "Output.txt";
	const char resultfilename[FILENAME_MAX] = "Results.txt";

public:
	// Implements Boostrap Method
	/*void Bootstrap()
	{   // N should be be defined here
		srand((unsigned)time(NULL));

		vector<string> group_0;
		vector<string> group_1;
		vector<string> group_2;
		int group_0_size = group_0.size();
		int group_1_size = group_1.size();
		int group_2_size = group_2.size();

		iter = stocks.begin();      // from stocks map to 3 group
		while (iter != stocks.end()) {
			if ((iter->second).getGroup() == "Low surprise group")
				group_0.push_back(iter->first);
			else if ((iter->second).getGroup() == "In Between group")
				group_1.push_back(iter->first);
			else if ((iter->second).getGroup() == "High surprise group")
				group_2.push_back(iter->first);
			else;
			iter++;
		}

		// double AAR0s[40], AAR1s[40],AAR2s[40];
		double CAAR0s[40], CAAR1s[40], CAAR2s[40];
		double CAARt_0[60], CAARt_1[60], CAARt_2[60];

		for (int i = 0; i < 40; i++)
		{
			vector<string> group_0_selected;
			vector<string> group_1_selected;
			vector<string> group_2_selected;
			vector<int> group_0_label(group_0_size);   // all 0 now, not selected; labeled 1 if selected
			vector<int> group_1_label(group_1_size);
			vector<int> group_2_label(group_2_size);

			// a. Randomly selecting 50 stocks from each group, total 150 stocks.
			matrix AART_0(1, 2N + 1);
			matrix AART_1(1, 2N + 1);
			matrix AART_2(1, 2N + 1);
			for (int j = 0; j < 50; j++)  // Need to make sure each group has >=50 stocks
			{
				int a = rand() % group_0_size;
				while (group_0_label[a] == 1) a = rand() % group_0_size;
				group_0_label[a] = 1;
				group_0_selected.push_back(group_0[a].getName);
				matrix m0(1, 2N + 1) = getStock(group_0[a].getName, N);  // Need to change the return to AR_it
				AART_0 += m0;

				a = rand() % group_1_size;
				while (group_1_label[a] == 1) a = rand() % group_1_size;
				group_1_label[a] = 1;
				group_1_selected.push_back(group_1[a].getName);
				matrix m1(1, 2N + 1) = getStock(group_1[a].getName, N);  // Need to change the return to AR_it
				AART_1 += m1;

				a = rand() % group_2_size;
				while (group_2_label[a] == 1) a = rand() % group_2_size;
				group_2_label[a] = 1;
				group_2_selected.push_back(group_2[a].getName);
				getStock(group_0[a].getName, N);
				matrix m2(1, 2N + 1) = getStock(group_2[a].getName, N);  // Need to change the return to AR_it
				AART_2 += m2;

				for (int k = 0; k < 2N + 1; k++)
				{
					CAARt_0[k] += AART_0.sum(k + 1);
					CAARt_1[k] += AART_1.sum(k + 1);
					CAARt_2[k] += AART_2.sum(k + 1);
				}
			}

			AART_0 *= 1 / 50;
			AART_1 *= 1 / 50;
			AART_2 *= 1 / 50;

			CAAR_0 = AART_0.sum(); CAAR0s[i] = CAAR_0;
			CAAR_1 = AART_1.sum(); CAAR1s[i] = CAAR_1;
			CAAR_2 = AART_2.sum(); CAAR2s[i] = CAAR_2;
		}
		double CAAR_0_mean = mean(CAAR_0s, 40);
		double CAAR_1_mean = mean(CAAR_1s, 40);
		double CAAR_2_mean = mean(CAAR_2s, 40);

		double CAAR_0_std = std(CAAR_0s, 40);
		double CAAR_1_std = std(CAAR_1s, 40);
		double CAAR_2_std = std(CAAR_2s, 40);



	};*/

	// Initialize Cookies and Crumbs
	void init_cookie_monster() {
		struct MemoryStruct data;
		data.memory = NULL;
		data.size = 0;
		
		// set up the program environment that libcurl needs 
		curl_global_init(CURL_GLOBAL_ALL);

		// curl_easy_init() returns a CURL easy handle 
		handle = curl_easy_init();
		// if everything's all right with the easy handle... 
		if (handle)
		{
			fp1 = fopen(outfilename, "w");
			if (sCookies.length() == 0 || sCrumb.length() == 0)
			{
				fp2 = fopen(resultfilename, "w");
				curl_easy_setopt(handle, CURLOPT_URL, "https://finance.yahoo.com/quote/AMZN/history");
				curl_easy_setopt(handle, CURLOPT_SSL_VERIFYPEER, 0);
				curl_easy_setopt(handle, CURLOPT_SSL_VERIFYHOST, 0);
				curl_easy_setopt(handle, CURLOPT_COOKIEJAR, "cookies.txt");
				curl_easy_setopt(handle, CURLOPT_COOKIEFILE, "cookies.txt");

				curl_easy_setopt(handle, CURLOPT_ENCODING, "");
				curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data);
				curl_easy_setopt(handle, CURLOPT_WRITEDATA, fp2);
				result = curl_easy_perform(handle);
				fclose(fp2);

				if (result != CURLE_OK)
				{
					// if errors have occurred, tell us what is wrong with result
					fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
					exit(1);
				}

				curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data2);
				curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void*)&data);

				// perform, then store the expected code in result
				result = curl_easy_perform(handle);

				if (result != CURLE_OK)
				{
					// if errors have occured, tell us what is wrong with result
					fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
					exit(1);
				}

				char cKey[] = "CrumbStore\":{\"crumb\":\"";
				char* ptr1 = strstr(data.memory, cKey);
				char* ptr2 = ptr1 + strlen(cKey);
				char* ptr3 = strstr(ptr2, "\"}");
				if (ptr3 != NULL)
					*ptr3 = NULL;

				sCrumb = ptr2;

				fp2 = fopen("cookies.txt", "r");
				char cCookies[100];
				if (fp2) {
					while (fscanf(fp2, "%s", cCookies) != EOF);
					fclose(fp2);
				}
				else
					cerr << "cookies.txt does not exists" << endl;

				sCookies = cCookies;
				free(data.memory);
				data.memory = NULL;
				data.size = 0;
			}

		}
		else
		{
		fprintf(stderr, "Curl init failed!\n");
		return exit(1);
		}

	}

	void goodbye_cookie_monster() {
		fclose(fp1);
		// cleanup since you've used curl_easy_init  
		curl_easy_cleanup(handle);

		// release resources acquired by curl_global_init() 
		curl_global_cleanup();

	}

	// Load IWB Data
	void loadIWB() {
		string startTime = getTimeinSeconds2("2020-01-01T16:00:00");
		string endTime = getTimeinSeconds2("2021-12-31T16:00:00");
		vector<string> symbolList;
		populateSymbolVector(symbolList);

		struct MemoryStruct data;
		data.memory = NULL;
		data.size = 0;

		FILE* fp1;
		const char result2filename[FILENAME_MAX] = "Result2.txt";

		CURL* handle;
		CURLcode result;

		// set up the program environment that libcurl needs 
		curl_global_init(CURL_GLOBAL_ALL);

		// curl_easy_init() returns a CURL easy handle 
		handle = curl_easy_init();

		// if everything's all right with the easy handle... 
		if (handle)
		{
			string sCookies, sCrumb;
			fp1 = fopen(result2filename, "w");
			string urlA = "https://query1.finance.yahoo.com/v7/finance/download/";
			string symbol = "IWB";
			string urlB = "?period1=";
			string urlC = "&period2=";
			string urlD = "&interval=1d&events=history";
			string url = urlA + symbol + urlB + startTime + urlC + endTime;
			const char* cURL = url.c_str();
			curl_easy_setopt(handle, CURLOPT_URL, cURL);


			fprintf(fp1, "%s\n", symbol.c_str());
			curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data);
			curl_easy_setopt(handle, CURLOPT_WRITEDATA, fp1);
			result = curl_easy_perform(handle);
			fprintf(fp1, "%c", '\n');

			//Check for errors
			if (result != CURLE_OK)
			{
				// if errors have occurred, tell us what is wrong with 'result'
				fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
				exit(1);
			}
			curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data2);
			curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void*)&data);
			result = curl_easy_perform(handle);

			if (result != CURLE_OK)
			{
				// if errors have occurred, tell what is wrong with result
				fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
				exit(1);
			}
			stringstream sData;
			sData.str(data.memory);
			string sValue, sDate;
			double dValue = 0;
			string line;
			getline(sData, line);
			// Keeps track of whether it's the first passage
			bool first_flag = true;
			// Keeps track of previous price
			double lastValue = 0;
			while (getline(sData, line)) {
				double ret = 0;
				sDate = line.substr(0, line.find_first_of(','));
				line.erase(line.find_last_of(','));
				sValue = line.substr(line.find_last_of(',') + 1);
				dValue = strtod(sValue.c_str(), NULL);
				if (first_flag) {
					ret = -999;
					lastValue = dValue;
				}
				else {
					ret = (dValue - lastValue) / lastValue;
				}
				IWB[sDate] = make_pair(dValue, ret);
			}
			fclose(fp1);
			free(data.memory);
			data.size = 0;
		}
		else
		{
			fprintf(stderr, "Curl init failed!\n");
			return exit(1);
		}

		// cleanup since you've used curl_easy_init  
		curl_easy_cleanup(handle);

		// release resources acquired by curl_global_init() 
		curl_global_cleanup();

	};

	// Load Stock EPS 
	void loadStockEPS() {

		std::string filename = "Surprise%.csv";
		// Create an input filestream
		std::ifstream myFile(filename);

		// Make sure the file is open
		if (!myFile.is_open()) throw std::runtime_error("Could not open file");

		// Helper vars
		std::string line, colname;
		std::string val;

		// Read data, line by line
		while (std::getline(myFile, line))
		{	
			// Temp Name Holder 
			std::string Name = "";
			std::string Dayzero = "";
			double Estimate_EPS = 0.0;
			double Reported_EPS = 0.0;
			double surprise = 0.0;
			// Create a stringstream of the current line
			std::stringstream ss(line);
			std::vector<std::string> temp;
			// Extract each integer
			while (ss >> val) {
				size_t pos = 0;
				std::string delimiter = ",";
				std::string token;
				int count = 0;
				while ((pos = val.find(delimiter)) != std::string::npos) {
					token = val.substr(0, pos);
					if (count == 0) {
						Name = token;
						count++;
					}
					else if (count == 1) {
						Dayzero = token;
						count++;
					}
					else if (count == 2) {
						Estimate_EPS = stod(token);
						count++;
					}
					else if (count == 3) {
						Reported_EPS = stod(token);
						count++;
					}
					else if (count == 4) {
						surprise = stod(token);
						count++;
					}
					val.erase(0, pos + delimiter.length());
				}
			}
			Stock tick = Stock(Name, -1, Estimate_EPS, Reported_EPS, surprise, Dayzero);
			stocks[Name] = tick;
			pq.push(tick);
		}
		int n = pq.size(); 
		int i = 0;
		// Sets the group of the stock according to the relative size in the priority queue
		while(!pq.empty()) {
			Stock asset = pq.top();
			if (i < n / 3) {
				stocks[asset.getName()].setGroup(0);
			}
			else if (i < 2 * n / 3) {
				stocks[asset.getName()].setGroup(1);
			}
			else {
				stocks[asset.getName()].setGroup(2);
			}
			i++;
			pq.pop();
		}

		// Close file
		myFile.close();
	};

	// Get Stock Information 
	std::vector<double> getStock(const std::string& ticker, int days) {
		std::vector<double> prices;
		if (stocks.find(ticker) == stocks.end()) {
			// not found
			extractStock(ticker, days);
			prices = stocks[ticker].getPerformance();
		}
		else {
			// found
			prices = stocks[ticker].getPerformance();
			// if stock data is not stored

			if (!stocks[ticker].checkStored()) {
				extractStock(ticker, days);
				prices = stocks[ticker].getPerformance();
			}
			else {
				// if we don't have enough data, we update with larger data set
				if (prices.size() < 2 * days + 1) {
					extractStock(ticker, days);
					prices = stocks[ticker].getPerformance();
				}
				// We note that if our current window is larger than the search window, only need to take a subsection of our data
				// This saves data search complexity
				else {
					int index_zero = prices.size() / 2;
					std::vector<double> temp;
					for (int i = index_zero - days; i <= index_zero + days; i++) {
						temp.push_back(prices[i]);
					}
					prices = temp;
				}
			}
		}
		return prices;
	}

	// Print Stock Information
	void printStock(const std::string& ticker, int days) {
		std::vector<double> data = getStock(ticker, days);
		stringstream buffer;
		if (!stocks[ticker].checkStored()) {
			std::cout << ticker << " : Not enough data points! Try smaller N" << endl;
			return;
		}
		std::cout << "Ticker: " << ticker << endl;
		for (int i = 0; i < 2*days + 1; i++) {
			buffer << stocks[ticker].getDate(i) << ": " << std::fixed << ::setprecision(6) << data[i] << endl;
		}
		std::cout << buffer.str() << endl;
	}

	// Uses libcurl to extract stock information
	void extractStock(const std::string& ticker, int days) {
		stocks[ticker].nowStored(true);
		//cout << "day 0" << stocks[ticke;r].getDay() << endl;
		time_t t = stotime(stocks[ticker].getDay());
		//cout << "t: " << t << endl;
		const time_t LATEST_DATE = time(0);
		string startTime = getTimeinSeconds(timetos(t - long(days) * 2.5 * 24 * 3600));
		string endTime = getTimeinSeconds(timetos(t + long(days) * 24 * 2.5 * 3600));
		
		struct MemoryStruct data;
		data.memory = NULL;
		data.size = 0;

		string urlA = "https://query1.finance.yahoo.com/v7/finance/download/";
		string symbol = ticker;
		string urlB = "?period1=";
		string urlC = "&period2=";
		string urlD = "&interval=1d&events=history&crumb=";
		string url = urlA + symbol + urlB + startTime + urlC + endTime + urlD + sCrumb;
		const char* cURL = url.c_str();
		const char* cookies = sCookies.c_str();
		curl_easy_setopt(handle, CURLOPT_COOKIE, cookies);
		curl_easy_setopt(handle, CURLOPT_URL, cURL);

		fprintf(fp1, "%s\n", symbol.c_str());
		curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data);
		curl_easy_setopt(handle, CURLOPT_WRITEDATA, fp1);
		result = curl_easy_perform(handle);
		fprintf(fp1, "%c", '\n');

		// Check for errors */
		if (result != CURLE_OK)
		{
			// if errors have occurred, tell us what is wrong with 'result'
			fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
			exit(1);
		}
		curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data2);
		curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void*)&data);
		result = curl_easy_perform(handle);

		if (result != CURLE_OK)
		{
			// if errors have occurred, tell us what is wrong with result
			fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(result));
			exit(1);
		}

		stringstream sData;
		sData.str(data.memory);
		string sValue, sDate;
		double dValue = 0;
		string line;
		getline(sData, line);
		stocks[ticker].resetData();
		// Keeps track of size of vector
		int count = 0;
		std::deque<std::string> temp_date;
		std::deque<std::double_t> temp_hist;
		// Keeps track of price before window for purpose of return
		double temp_p = 0.0;
		while (getline(sData, line)) {
			sDate = line.substr(0, line.find_first_of(','));
			line.erase(line.find_last_of(','));
			sValue = line.substr(line.find_last_of(',') + 1);
			dValue = strtod(sValue.c_str(), NULL);
			//cout << sDate << " " << std::fixed << ::setprecision(6) << dValue << endl;
			// We have this rolling window of 2*days+1 observations. When we reach day zero, we take this window and add it to our database
			temp_date.push_back(sDate);
			temp_hist.push_back(dValue);
			if (temp_date.size() > 2 * days + 1) {
				temp_date.pop_front();
				// This will always be the last price before our window
				temp_p = temp_hist.front();
				temp_hist.pop_front();
			}
			// We convert sDate to see if we have passed day zero
			string delimiter = "-";
			int pos = sDate.find(delimiter);
			int year = stoi(sDate.substr(0, pos));
			string temp = sDate.substr(pos + 1, sDate.size());
			pos = temp.find(delimiter);
			int month = stoi(temp.substr(0, pos));
			int day = stoi(temp.substr(pos + 1, temp.size()));

			// Once we have passed day zero, we shift our window N days more so that our day zero is in the center.
			if (dateToTimeT(month, day, year) > t) {
				count++;
			}
			if (count >= days) {
				break;
			}
		}
		// We add the two deques into our map data
		if (temp_hist.size() == 2 * days + 1) {
			for (int i = 0; i < 2 * days + 1; i++) {
				if (i == 0) {
					stocks[ticker].addData(temp_hist[i], (temp_hist[i] - temp_p) / temp_p, temp_date[i]);
				}
				else {
					stocks[ticker].addData(temp_hist[i], (temp_hist[i] - temp_hist[i - 1]) / temp_hist[i - 1], temp_date[i]);
				}
			}
		}
		else {
			// Not enough data points! Try smaller N
			stocks[ticker].resetData();
			stocks[ticker].nowStored(false);
		}
		//}
		free(data.memory);
		data.size = 0;

	}

	/*
	// Returns AAR 
	double getAAR(int group) {
		return matrix[group][0];
	}

	// Returns AAR_STD
	double getAAR_STD(int group) {
		return matrix[group][1];
	}

	// Returns CAAR 
	double getCAAR(int group) {
		return matrix[group][2];
	}

	// Returns CAAR_STD
	double getCAAR_STD(int group) {
		return matrix[group][3];
	}

	// Returns AAR 
	void setAAR(int group, double val) {
		matrix[group][0] = val;
	}

	// Returns AAR_STD
	void setAAR_STD(int group, double val) {
		matrix[group][1] = val;
	}

	// Returns CAAR 
	double getCAAR(int group, double val) {
		matrix[group][2] = val;
	}

	// Returns CAAR_STD
	double setCAAR_STD(int group, double val) {
		matrix[group][3] = val;
	}
	*/

	// Pull all data for stocks
	void pullAll(int days) {
		
		
		for (auto c : stocks) {
			
			printStock(c.first, days);
		}
		
		
		//FAILED ATTEMPT #1
		// create thread pool with 4 worker threads
		/*
		ThreadPool pool(2);

		// enqueue and store future
		for (auto c : stocks) {
			pool.enqueue(&Interface::printStock, this, c.first, days);
		}
		*/

		//FAILED ATTEMPT #2
		/*
		std::vector<std::thread> threads;
		for (auto c : stocks) {
			threads.push_back(std::thread(&Interface::printStock, this, c.first, days));
		}

		for (auto& th : threads) {
			th.join();
		}
		*/
	}

	// Returns the info of the stock
	void getInfo(const std::string& ticker, int days) {
		std::vector<double> data = getStock(ticker, days);
		if (!stocks[ticker].checkStored()) {
			std::cout << ticker <<  " : Not enough data points! Try smaller N" << endl;
			return;
		}
		std::cout << "Ticker: " << ticker << endl;
		std::vector<double> returns;
		std::cout << "Group: " << stocks[ticker].getGroup() << endl;
		std::cout << "Earning Announcement Date: " << stocks[ticker].getDay() << endl;
		std::cout << "Period Ending" << endl;
		// TO DO: Fill out rest of information
		std::cout << "Date | Price | Returns";
		stringstream buffer;
		for (int i = 0; i < 2 * days + 1; i++) {
			if (i > 0) {
				returns.push_back((data[i] - data[i - 1]) / (data[i - 1]) * 100);
			}
			else {
				returns.push_back(-999);
			}
			buffer << stocks[ticker].getDate(i) << ": " << data[i] << "| Returns: "
				<< returns[i] << endl;
		}
		std::cout << buffer.str() << endl;
	}

};
