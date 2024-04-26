// Final_Project.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include "Interface.h"
#include <iostream>

int main()
{
    //std::ios_base::sync_with_stdio(false);
    Interface exchange = Interface();
    exchange.loadStockEPS();
    exchange.init_cookie_monster();
    exchange.loadIWB();
    exchange.printStock("CIEN", 60);
    exchange.printStock("ACC", 30);


    // Menu for our interface
    std::cout << "STOCK TERMINAL" << std::endl << std::endl;
    std::cout << "We have the following menu options:" << endl;

    std::cout << "(1) Historical Price Data for all stocks" << endl;
    std::cout << "(2) Stock information for a given stock of a group" << endl;
    std::cout << "(3) Show AAR, AAR - SD, CAARand CAAR - STD for one group." << endl;
    std::cout << "(4) Show the Excel or gnuplot graph with CAAR for all 3 groups." << endl;
    std::cout << "(5) exit program" << endl;

    char x;
    std::cin >> x;

    int n;


    std::string ticker;
    while (true) {
        switch (x) {
        case '1':
            std::cout << "N: ";
            std::cin >> n;
            if (n >= 30) {
                exchange.pullAll(n);
            }
            else {
                std::cout << "At least 30 days are required" << endl;
                exit(1);
            }
        case '2':
            std::cout << "Ticker name: ";
            std::cin >> ticker;
            std::cout << "N: ";
            exchange.printStock(ticker, n);
        case '3':
            std::cout << "" << endl;
        case '4':
            std::cout << "" << endl;
        case '5':
            exchange.goodbye_cookie_monster();
            exit(0);
        default:
            std::cout << "Try again" << endl;
            std::cin >> n;
        }
    }
}
