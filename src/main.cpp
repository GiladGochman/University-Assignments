#include "../include/WareHouse.h"
#include "../include/Customer.h"
#include <iostream>

using namespace std;

WareHouse extern *backup = nullptr;

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        std::cout << "usage: warehouse <config_path>" << std::endl;
        return 0;
    }
    string configurationFile = argv[1];
    WareHouse wareHouse(configurationFile);
    wareHouse.start();
    if(backup!=nullptr){
    	delete backup;
    	backup = nullptr;
    }
    return 0;
}