#include <stdio.h>
#include <string> 
#include <iostream>
#include <sstream>  
#include <vector>
#include <locale>
#include <iomanip>
#include <fstream>

#include "curl\curl.h"

using namespace std;

const char* cIWB1000SymbolFile = "Russell_1000_component_stocks.csv";

void populateSymbolVector(vector<string>& symbols)
{
	ifstream fin;
	fin.open(cIWB1000SymbolFile, ios::in);
	string line, name, symbol;
	while (!fin.eof())
	{
		getline(fin, line);
		stringstream sin(line);
		getline(sin, name, ',');
		getline(sin, symbol);
		symbols.push_back(symbol);
	}
}

int write_data(void* ptr, int size, int nmemb, FILE* stream)
{
	size_t written;
	written = fwrite(ptr, size, nmemb, stream);
	return (int)written;
}

struct MemoryStruct {
	char* memory;
	size_t size;
};

void* myrealloc(void* ptr, size_t size)
{
	if (ptr)
		return realloc(ptr, size);
	else
		return malloc(size);
}

int write_data2(void* ptr, size_t size, size_t nmemb, void* data)
{
	size_t realsize = size * nmemb;
	struct MemoryStruct* mem = (struct MemoryStruct*)data;
	mem->memory = (char*)myrealloc(mem->memory, mem->size + realsize + 1);
	if (mem->memory) {
		memcpy(&(mem->memory[mem->size]), ptr, realsize);
		mem->size += realsize;
		mem->memory[mem->size] = 0;
	}
	return (int)realsize;
}

string getTimeinSeconds(string Time)
{
	std::tm t = { 0 };
	std::istringstream ssTime(Time);
	char time[100];
	memset(time, 0, 100);
	if (ssTime >> std::get_time(&t, "%a %b %d %H:%M:%S %Y"))
	{
//		cout << std::put_time(&t, "%c %Z") << "\n"
//			<< std::mktime(&t) << "\n";
		sprintf(time, "%lld", mktime(&t));
		return string(time);
	}
	else
	{
		cout << "Parse failed\n";
		return "";
	}
}

string getTimeinSeconds2(string Time)
{
	std::tm t = { 0 };
	std::istringstream ssTime(Time);
	char time[100];
	memset(time, 0, 100);
	if (ssTime >> std::get_time(&t, "%Y-%m-%dT%H:%M:%S"))
	{
		cout << std::put_time(&t, "%c %Z") << "\n"
			<< std::mktime(&t) << "\n";
		sprintf(time, "%lld", mktime(&t));
		return string(time);
	}
	else
	{
		cout << "Parse failed\n";
		return "";
	}
}