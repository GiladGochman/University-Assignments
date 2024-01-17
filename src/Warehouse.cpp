#include "../include/WareHouse.h"
#include <iostream>
#include <fstream>
#include <string>

class BaseAction;
class Volunteer;
class WareHouse;

// Warehouse responsible for Volunteers, Customers and Actions.

WareHouse::WareHouse(const string &configFilePath)
{
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
        if (!line.empty())
        {
            // Find the position of #
            size_t posHash = line.find('#');
            std::string partBeforeHash;
            // Extract the part before #
            if (posHash != std::string::npos)
                partBeforeHash = line.substr(0, posHash);

            // Trim leading whitespace from the line
            std::string trimmedLine = trimLeadingWhitespace(partBeforeHash);
            if (!trimmedLine.empty())
                std::cout << trimmedLine << std::endl;

            // Find the position of space
            // size_t posSpace = partBeforeHash.find(' ');

            // while (!partBeforeHash.empty() & posSpace == 0 & posSpace != std::string::npos)
            // {
            //     // Extract the part before #
            //     std::string partBeforeHash = partBeforeHash.substr(1, 0);
            //     posSpace = partBeforeHash.find(' ');
            //     // std::cout << posSpace << std::endl;
            // }
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

// Function to trim leading whitespace from a string
std::string WareHouse::trimLeadingWhitespace(const std::string &str)
{
    size_t firstNonSpace = str.find_first_not_of(" \t");
    if (firstNonSpace == std::string::npos)
    {
        // The string is all spaces, return an empty string
        return "";
    }
    return str.substr(firstNonSpace);
}
