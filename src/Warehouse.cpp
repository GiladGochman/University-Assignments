#include "../include/WareHouse.h"
#include "../include/Volunteer.h"
#include "../include/Customer.h"
#include "../include/Order.h"
#include "../include/Action.h"
#include <iostream>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>

extern WareHouse *backup;
class BaseAction;
class Volunteer;
class WareHouse;

// Warehouse responsible for Volunteers, Customers and Actions.

WareHouse::WareHouse(const string &configFilePath) : isOpen(false), customerCounter(0), volunteerCounter(0), orderCounter(0)

{
    parseFile(configFilePath);
}

WareHouse::WareHouse(const WareHouse &other) : isOpen(other.isOpen), customerCounter(other.customerCounter), volunteerCounter(other.volunteerCounter), orderCounter(other.orderCounter)
{
    for (auto customer : other.customers)
    {
        customers.push_back(customer->clone());
    }

    for (auto orderP : other.pendingOrders)
    {
        pendingOrders.push_back(orderP->clone());
    }

    for (auto orderV : other.vol)
    {
        vol.push_back(orderV->clone());
    }

    for (auto orderC : other.completedOrders)
    {
        completedOrders.push_back(orderC->clone());
    }

    for (auto vol : other.volunteers)
    {
        volunteers.push_back(vol->clone());
    }

    for (auto action : other.actionsLog)
    {
        actionsLog.push_back(action->clone());
    }
}

WareHouse::~WareHouse()
{
    for (auto customer : customers)
    {
        delete customer;
    }

    customers.clear();

    for (auto vol : volunteers)
    {
        delete vol;
    }

    volunteers.clear();

    for (auto orderP : pendingOrders)
    {
        delete orderP;
    }

    pendingOrders.clear();

    for (auto orderV : vol)
    {
        delete orderV;
    }

    vol.clear();

    for (auto orderC : completedOrders)
    {
        delete orderC;
    }

    completedOrders.clear();

    for (auto action : actionsLog)
    {
        delete action;
    }

    actionsLog.clear();
}

WareHouse &WareHouse::operator=(const WareHouse &other)
{
    if (this != &other)
    {
        isOpen = other.isOpen;
        volunteerCounter = other.volunteerCounter;
        orderCounter = other.orderCounter;
        customerCounter = other.customerCounter;

        for (auto customer : customers)
        {
            delete customer;
        }

        customers.clear();

        for (auto vol : volunteers)
        {
            delete vol;
        }

        volunteers.clear();

        for (auto orderP : pendingOrders)
        {
            delete orderP;
        }

        pendingOrders.clear();

        for (auto orderV : vol)
        {
            delete orderV;
        }

        vol.clear();

        for (auto orderC : completedOrders)
        {
            delete orderC;
        }

        completedOrders.clear();

        for (auto action : actionsLog)
        {
            delete action;
        }

        actionsLog.clear();

        for (auto customer : other.customers)
        {
            customers.push_back(customer->clone());
        }

        for (auto orderP : other.pendingOrders)
        {
            pendingOrders.push_back(orderP->clone());
        }

        for (auto orderV : other.vol)
        {
            vol.push_back(orderV->clone());
        }

        for (auto orderC : other.completedOrders)
        {
            completedOrders.push_back(orderC->clone());
        }

        for (auto vol : other.volunteers)
        {
            volunteers.push_back(vol->clone());
        }

        for (auto action : other.actionsLog)
        {
            actionsLog.push_back(action->clone());
        }
    }

    return *this;
}

WareHouse::WareHouse(WareHouse &&other) : isOpen(other.isOpen), customerCounter(other.customerCounter), volunteerCounter(other.volunteerCounter), orderCounter(other.orderCounter)
{
    customers = std::move(other.customers);
    vol = std::move(other.vol);
    volunteers = std::move(other.volunteers);
    pendingOrders = std::move(other.pendingOrders);
    completedOrders = std::move(other.completedOrders);
    actionsLog = std::move(other.actionsLog);

    // for(auto customer:other.customers){
    //     customer = nullptr;
    // }

    // for(auto ord: other.vol){
    //     ord = nullptr;
    // }

    // for(auto vol : other.volunteers){
    //     vol = nullptr;
    // }

    // for(auto ord : other.pendingOrders){
    //     ord = nullptr;
    // }

    // for(auto ord : other.completedOrders){
    //     ord = nullptr;
    // }

    // for(auto action : other.actionsLog){
    //     action = nullptr;
    // }
}

WareHouse &WareHouse::operator=(WareHouse &&other)
{
    if (this != &other)
    {
        isOpen = other.isOpen;
        volunteerCounter = other.volunteerCounter;
        orderCounter = other.orderCounter;
        customerCounter = other.customerCounter;
        customers = std::move(other.customers);
        vol = std::move(other.vol);
        volunteers = std::move(other.volunteers);
        pendingOrders = std::move(other.pendingOrders);
        completedOrders = std::move(other.completedOrders);
        actionsLog = std::move(other.actionsLog);
        // customers=other.customers;
        // volunteers=other.volunteers;
        // pendingOrders=other.pendingOrders;
        // vol=other.vol;
        // completedOrders=other.completedOrders;
        // actionsLog=other.actionsLog;

        // for(auto customer:other.customers){
        //     customer = nullptr;
        // }

        // for(auto ord: other.vol){
        //     ord = nullptr;
        // }

        // for(auto vol : other.volunteers){
        //     vol = nullptr;
        // }

        // for(auto ord : other.pendingOrders){
        //     ord = nullptr;
        // }

        // for(auto ord : other.completedOrders){
        //     ord = nullptr;
        // }

        // for(auto action : other.actionsLog){
        //     action=nullptr;
        // }
    }
    return *this;
}

void WareHouse::start()
{

    open();
    while (isOpen)
    {
        // breaking down the input

            string line;
            getline(cin,line);
            std::istringstream iss(line);
           
            vector<string> decodedString;
            string word;
            while (getline(iss, word, ' '))
            {
                decodedString.push_back(word);
            }

            if (decodedString[0] == "customer")
            {
                AddCustomer *action = new AddCustomer(decodedString[1], decodedString[2], std::stoi(decodedString[3]), std::stoi(decodedString[4]));
                action->act(*this);
                actionsLog.push_back(action);
            }
            if (decodedString[0] == "order")
            {
                
                AddOrder *action = new AddOrder(stoi(decodedString[1]));
                action->act(*this);
                actionsLog.push_back(action);
            }

            if (decodedString[0] == "step")
            {
                SimulateStep *action = new SimulateStep(std::stoi(decodedString[1]));
                action->act(*this);
                actionsLog.push_back(action);
            }
            // if (decodedString[0] == "backup")
            // {
            //     BackupWareHouse *action = new BackupWareHouse();
            //     action->act(*this);
            //     actionsLog.push_back(action);
            // }
            // if (decodedString[0] == "restore")
            // {
            //     RestoreWareHouse *action = new RestoreWareHouse();
            //     action->act(*this);
            //     actionsLog.push_back(action);
            // }
            if (decodedString[0] == "log")
            {
                PrintActionsLog *action = new PrintActionsLog();
                action->act(*this);
                actionsLog.push_back(action);
            }
            // if (decodedString[0] == "close")
            // {
            //     Close *action = new Close();
            //     action->act(*this);
            // }
            if (decodedString[0] == "volunteerStatus")
            {
                PrintVolunteerStatus *action = new PrintVolunteerStatus(std::stoi(decodedString[1]));
                action->act(*this);
                actionsLog.push_back(action);
            }
            if (decodedString[0] == "orderStatus")
            {
                PrintOrderStatus *action = new PrintOrderStatus(std::stoi(decodedString[1]));
                action->act(*this);
                actionsLog.push_back(action);
            }
            if (decodedString[0] == "customerStatus")
            {
                PrintCustomerStatus *action = new PrintCustomerStatus(std::stoi(decodedString[1]));
                action->act(*this);
                actionsLog.push_back(action);
            }
                cout << pendingOrders.size() << vol.size() << completedOrders.size() << endl;
    }

}

const vector<BaseAction *> &WareHouse::getActionsLog() const
{
    return actionsLog;
}

const vector<Customer *> &WareHouse::getCustomersVector() const
{
    return customers;
}

const vector<Order *> &WareHouse::getPendingOrdersVector() const
{
    return pendingOrders;
}

const vector<Order *> &WareHouse::getInProgressVector() const
{
    return vol;
}

const vector<Order *> &WareHouse::getCompletedOrdersVector() const
{
    return completedOrders;
}

const vector<Volunteer *> &WareHouse::getVolunteerVector() const
{
    return volunteers;
}

void WareHouse::addOrder(Order *order)
{
    pendingOrders.push_back(order);
    ++orderCounter;
}

void WareHouse::addAction(BaseAction *action)
{
    actionsLog.push_back(action);
}

void WareHouse::printActionsLogs()
{
    for (BaseAction *action : actionsLog)
    {
        cout << action->toString() << endl;
    }
    // need to implement baseactions class for that
}

void WareHouse::open()
{
    isOpen = true;
    cout << "The Warehouse is open" << endl;
}

void WareHouse::close()
{
    for (Order *order : pendingOrders)
    {
        cout << order->toString() << endl;
    }

    for (Order *order : vol)
    {
        cout << order->toString() << endl;
    }

    for (Order *order : completedOrders)
    {
        cout << order->toString() << endl;
    }
    isOpen = false;
    cout << "Closing the Warehouse" << endl;
}

Customer &WareHouse::getCustomer(int customerId) const
{
    return *customers[customerId];
}

Volunteer &WareHouse::getVolunteer(int volunteerId) const{
    for(auto volunteer : volunteers){
        if(volunteer->getId()==volunteerId) return *volunteer;
    }
}

Order &WareHouse::getOrder(int orderId) const
{
    for (Order *order : pendingOrders)
    {
        if (order->getId() == orderId)
            return *order;
    }

    for (Order *order : vol)
    {
        if (order->getId() == orderId)
            return *order;
    }

    for (Order *order : completedOrders)
    {
        if (order->getId() == orderId)
            return *order;
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

bool WareHouse::checkIfCustomerExsists(int id)
{
    return id < customerCounter && id >= 0; // id < customerCounter -> because the ids start from 0 (when couner=1)
}
int WareHouse::getOrderCounter()
{
    return orderCounter;
}

void WareHouse::setCustomerCounter(int increase)
{
    customerCounter = customerCounter + increase;
}

void WareHouse::setVolunteerCounter(int increase)
{
    volunteerCounter = volunteerCounter + increase;
}

void WareHouse::addCustomer(Customer *customer)
{
    customers.push_back(customer);
    setCustomerCounter(1);
}
int WareHouse::getCustomerCounter()
{
    return customerCounter;
}

bool WareHouse::checkIfOrderExsists(int orderId)
{
    return orderId >= 0 && orderId < orderCounter; //  orderId < orderCounter -> because the ids start from 0 (when couner=1)
}

 void WareHouse::assignOrder(vector<Order *>::const_iterator it)
{

    vol.push_back(*it);
    // int searchValue = order->getId();
    // auto it = std::find_if(pendingOrders.begin(), pendingOrders.end(), [searchValue](const Order *ptr)
    //                        { return ptr != nullptr && ptr->getId() == searchValue; });
    auto newit=pendingOrders.erase(it);
}

void WareHouse::moveFromVolunteerOrder(vector<Order *>::const_iterator it){
    Order *order=*it;
    vol.erase(it);
    if(order->getStatus()==OrderStatus::COLLECTING) pendingOrders.push_back(order);
    else if(order->getStatus() == OrderStatus::DELIVERING){
        order->setStatus(OrderStatus::COMPLETED);
        completedOrders.push_back(order);
    }
}

vector<Volunteer *>::const_iterator &WareHouse::fireVolunteer(vector<Volunteer *>::const_iterator it) {
    vector<Volunteer*>::const_iterator itReturn =volunteers.erase(it);
    return itReturn;
}

