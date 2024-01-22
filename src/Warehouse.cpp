#include "../include/WareHouse.h"
#include "../include/Volunteer.h"
#include "../include/Customer.h"
#include <iostream>
#include <fstream>
#include <string>

class BaseAction;
class Volunteer;
class WareHouse;

// Warehouse responsible for Volunteers, Customers and Actions.

WareHouse::WareHouse(const string &configFilePath) : isOpen(true), customerCounter(0), volunteerCounter(0)

{
    // Question: how to initialize customers vector?
    // vector<Customer *> customers;
    // customers = vector<Customer *>();

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
            {
                std::cout << trimmedLine << std::endl;

                // Now parse each line and insert into database
                // Vector to store parsed words
                std::vector<std::string> words;

                // Find the position of the first space in the string
                size_t pos = trimmedLine.find(' ');

                // Loop until no more spaces are found
                while (pos != std::string::npos)
                {
                    // Extract the word before the space
                    std::string word = trimmedLine.substr(0, pos);

                    // Add the word to the vector
                    words.push_back(word);

                    // Remove the processed part (including the space)
                    trimmedLine = trimmedLine.substr(pos + 1);

                    // Find the position of the next space
                    pos = trimmedLine.find(' ');
                }

                // Add the last word (or the only word if no space is found)
                words.push_back(trimmedLine);

                // Now the line is stored word by word in words variable.
                // for customer

                // Inset data
                if (words[0] == "customer")
                {
                    // words[0] contains the role
                    // words[1] contains the name
                    // words[2] contains the type
                    // words[3] contains the distance
                    // words[4] contains the max orders number
                    try
                    {
                        if (words[2] == "soldier")
                        {
                            customers.push_back(new SoldierCustomer(customerCounter, words[1], std::stoi(words[3]), std::stoi(words[4])));
                            ++customerCounter;
                        }
                        else if (words[2] == "civilian")
                        {
                            customers.push_back(new CivilianCustomer(customerCounter, words[1], std::stoi(words[3]), std::stoi(words[4])));
                            ++customerCounter;
                        }
                    }
                    catch (const std::exception &e)
                    {
                        std::cerr << "Wrong syntax, please check configuration file." << '\n';
                    }
                }
                else if (words[0] == "volunteer")
                {
                    try
                    {
                        if (words[2] == "collector") // Recieves a 4 word input
                        {
                            volunteers.push_back(new CollectorVolunteer(volunteerCounter, words[1], std::stoi(words[3])));
                            ++volunteerCounter;
                        }
                        else if (words[2] == "limited_collector") // Recieves a 5 word input
                        {
                            volunteers.push_back(new LimitedCollectorVolunteer(volunteerCounter, words[1], std::stoi(words[3]), std::stoi(words[4])));
                            ++volunteerCounter;
                        }
                        else if (words[2] == "driver") // Recieves a 5 word input
                        {
                            volunteers.push_back(new DriverVolunteer(volunteerCounter, words[1], std::stoi(words[3]), std::stoi(words[4])));
                            ++volunteerCounter;
                        }
                        else if (words[2] == "limited_driver") // Recieves a 6 word input
                        {
                            volunteers.push_back(new LimitedDriverVolunteer(volunteerCounter, words[1], std::stoi(words[3]), std::stoi(words[4]), std::stoi(words[5])));
                            ++volunteerCounter;
                        }
                    }
                    catch (const std::exception &e)
                    {
                        std::cerr << "Wrong syntax, please check configuration file." << '\n';
                    }
                }
                else
                {
                    // Code to execute if none of the conditions match
                    std::cout << "Wrong syntax, please check configuration file." << std::endl;
                }
            }
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
