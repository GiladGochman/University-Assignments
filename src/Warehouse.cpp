#include "../include/WareHouse.h"
#include <iostream>
#include <fstream>
#include <string>

class BaseAction;
class Volunteer;

// Warehouse responsible for Volunteers, Customers and Actions.

WareHouse::WareHouse(const string &configFilePath)
{
    std::cout << configFilePath << std::endl;
    std::fstream inputFile(configFilePath);

    if (!inputFile.is_open())
    {
        std::cerr << "Error opening the file." << std::endl;
        return;
    }

    // Variable to store each line
    std::string line;

    // Read and parse the file content
    while (std::getline(inputFile, line))
    {
        // Find the position of #
        size_t posHash = line.find('#');

        // Extract the part before #
        std::string partBeforeHash = line.substr(0, posHash);

        size_t posSpace = line.find(' ');

        if (!partBeforeHash.empty() & posSpace != 0)
        {
            // Find the position of space

            std::cout << partBeforeHash << std::endl;
        }
    }

    // Close the file
    inputFile.close();
}
// void start();
// const vector<BaseAction*> &getActionsLog() const;
// void addOrder(Order* order);
// void addAction(BaseAction* action);
// void printActionsLogs();
// Customer &getCustomer(int customerId) const;
// Volunteer &getVolunteer(int volunteerId) const;
// Order &getOrder(int orderId) const;
// void close();
// void open();

// bool isOpen;
// vector<BaseAction*> actionsLog;
// vector<Volunteer*> volunteers;
// vector<Order*> pendingOrders;
// vector<Order*> vol;
// vector<Order*> completedOrders;
// vector<Customer*> customers;
// int customerCounter; //For assigning unique customer IDs
// int volunteerCounter; //For assigning unique volunteer IDs