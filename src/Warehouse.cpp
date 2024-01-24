#include "../include/WareHouse.h"
#include "../include/Volunteer.h"
#include "../include/Customer.h"
#include "../include/Order.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>

class BaseAction;
class Volunteer;
class WareHouse;

// Warehouse responsible for Volunteers, Customers and Actions.

WareHouse::WareHouse(const string &configFilePath) : isOpen(true), customerCounter(0), volunteerCounter(0), orderCounter(0)

{
    parseFile(configFilePath);
}

WareHouse::WareHouse(const WareHouse &other): isOpen(other.isOpen), customerCounter(other.customerCounter), volunteerCounter(other.volunteerCounter), orderCounter(other.orderCounter){
    for(auto customer: other.customers){
        customers.push_back(customer->clone());
    }

    for(auto vol : other.volunteers){
        volunteers.push_back(vol->clone());
    }

    for(auto orderP : other.pendingOrders){
        pendingOrders.push_back(orderP->clone());
    }

    for(auto orderV : other.vol){
        vol.push_back(orderV->clone());
    }

    for(auto orderC : other.completedOrders){
        completedOrders.push_back(orderC->clone());
    }

    for(auto vol: other.volunteers){
        volunteers.push_back(vol->clone());
    }
}

void WareHouse::start()
{
    while (isOpen)
    {
        string s;
        cin >> s;
        std::istringstream iss(s);
        vector<string> decodedString;
        string word;
        while(getline(iss,word,' ')){
            decodedString.push_back(word);
        }
        for(int i=0; i<decodedString.size(); i++){
            cout << decodedString[i] << endl;
        }
        // now the first word is about the action and the others are the parameters
        // switch cases..
    }
}

const vector<BaseAction *> &WareHouse::getActionsLog() const{
    return actionsLog;
}

void WareHouse::addOrder(Order *order){
    pendingOrders.push_back(order);
}

void WareHouse::addAction(BaseAction *action){
    actionsLog.push_back(action);
}

void WareHouse::printActionsLogs(){
    // for(BaseAction *action : actionsLog){
    //     cout<< *action.toString() <<endl;
    // }
    //need to implement baseactions class for that
}

Customer &WareHouse::getCustomer(int customerId) const{
    return *customers[customerId];
} 

Order &WareHouse::getOrder(int orderId) const{
    for(Order *order:pendingOrders){
        if(order->getId()==orderId) return *order;
    }

    for(Order *order:vol){
        if(order->getId()==orderId) return *order;
    }

    for(Order *order:completedOrders){
        if(order->getId()==orderId) return *order;
    }

}

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

void WareHouse::parseFile(const string &filePath)
{
    std::fstream inputFile(filePath);

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
                std::istringstream iss(trimmedLine);
                std::vector<std::string> words;
                std::string word;
                // breaking down the line into words.
                while (std::getline(iss, word, ' '))
                {
                    words.push_back(word);
                }
                // Add the last word (or the only word if no space is found)
                // words.push_back(trimmedLine);

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

bool WareHouse::checkIfCustomerExsists(int id){
    return id < customerCounter;
}