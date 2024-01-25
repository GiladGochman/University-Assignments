#include "../include/WareHouse.h"
#include "../include/Customer.h"
#include <iostream>

using namespace std;

WareHouse *backup = nullptr;

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        std::cout << "usage: warehouse <config_path>" << std::endl;
        return 0;
    }
    string configurationFile = argv[1];
    WareHouse wareHouse(configurationFile);
    std::cout << wareHouse.getCustomer(1).getName() << std::endl;
    backup = new WareHouse(wareHouse);
    std::cout << wareHouse.getCustomer(1).getName() << std::endl;
    // wareHouse.start();
    if(backup!=nullptr){
    	delete backup;
    	backup = nullptr;
    }
    return 0;
}